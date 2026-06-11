#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path('/home/laia/gridcode-protocol-hub')

ALLOWED_PROCESSES = {
    'webasto': {
        'script': ROOT / 'scripts' / 'webasto_unite_strict_playwright.py',
        'required_input_keys': [
            'run_id', 'charger_ip', 'charger_label', 'username', 'password', 'ocpp_endpoint'
        ],
    },
    'cpms': {
        'script': ROOT / 'scripts' / 'cpms_wings_create_charger.py',
        'required_input_keys': [
            'base_url', 'username', 'password', 'charger_name', 'charger_id'
        ],
    },
    'nuba': {
        'script': ROOT / 'scripts' / 'run_nuba_playwright_v1.py',
        'required_input_keys': [
            'base_url', 'username', 'password'
        ],
    },
}


@dataclass
class RunResult:
    status: str
    process: str
    command: list[str]
    exit_code: int
    input_sha256: str
    output_json: str
    started_at: str
    finished_at: str
    stdout: str
    stderr: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def validate_contract(process: str, data: dict[str, Any]) -> None:
    required = ALLOWED_PROCESSES[process]['required_input_keys']
    missing = [k for k in required if data.get(k) in (None, '')]
    if missing:
        raise ValueError(f'contract_violation_missing_keys:{",".join(missing)}')


def build_cmd(process: str, input_path: Path, output_path: Path) -> list[str]:
    py = '/home/laia/.venv/bin/python'
    if process == 'nuba':
        d = load_json(input_path)
        cmd = [
            py,
            str(ALLOWED_PROCESSES[process]['script']),
            '--base-url', str(d['base_url']),
            '--username', str(d['username']),
            '--password', str(d['password']),
            '--output', str(output_path),
        ]
        if d.get('creator_filter'):
            cmd += ['--creator-filter', str(d['creator_filter'])]
        if d.get('open_teleport_if_available', False):
            cmd += ['--open-teleport']
        return cmd

    return [
        py,
        str(ALLOWED_PROCESSES[process]['script']),
        '--input', str(input_path),
        '--output', str(output_path),
    ]


def run_once(process: str, input_path: Path, output_path: Path, timeout: int) -> RunResult:
    started = now_iso()
    input_hash = sha256_file(input_path)

    env = os.environ.copy()
    env['PYTHONPATH'] = '.'

    cmd = build_cmd(process, input_path, output_path)
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    finished = now_iso()

    status = 'ok' if proc.returncode == 0 else 'error'
    if not output_path.exists():
        status = 'error'

    return RunResult(
        status=status,
        process=process,
        command=cmd,
        exit_code=proc.returncode,
        input_sha256=input_hash,
        output_json=str(output_path),
        started_at=started,
        finished_at=finished,
        stdout=proc.stdout[-12000:],
        stderr=proc.stderr[-12000:],
    )


def compare_outputs(paths: list[Path]) -> dict[str, Any]:
    # Compara salidas ignorando timestamps y rutas de artifacts
    normalized = []
    for p in paths:
        d = load_json(p)
        for k in ('started_at', 'ended_at', 'finished_at'):
            if k in d:
                d[k] = '<time>'
        if 'artifacts' in d:
            d['artifacts'] = '<artifacts>'
        normalized.append(json.dumps(d, ensure_ascii=False, sort_keys=True))

    base = normalized[0]
    equal = all(x == base for x in normalized[1:])
    return {
        'replicable': equal,
        'runs': len(paths),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description='Orquestador productivo determinista (sin variaciones)')
    ap.add_argument('--process', choices=sorted(ALLOWED_PROCESSES.keys()), required=True)
    ap.add_argument('--input', required=True)
    ap.add_argument('--output-dir', default=str(ROOT / 'out' / 'production-orchestrator'))
    ap.add_argument('--repeat', type=int, default=1)
    ap.add_argument('--timeout', type=int, default=420)
    args = ap.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(json.dumps({'status': 'error', 'error': 'input_not_found'}))
        return 2

    data = load_json(input_path)
    try:
        validate_contract(args.process, data)
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': str(e)}))
        return 2

    out_dir = Path(args.output_dir) / args.process / datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir.mkdir(parents=True, exist_ok=True)

    run_results: list[RunResult] = []
    output_paths: list[Path] = []

    for i in range(1, args.repeat + 1):
        out_json = out_dir / f'run_{i:02d}.json'
        rr = run_once(args.process, input_path, out_json, args.timeout)
        run_results.append(rr)
        output_paths.append(out_json)
        if rr.status != 'ok':
            break

    all_ok = all(r.status == 'ok' for r in run_results)
    replicability = compare_outputs(output_paths) if all_ok and len(output_paths) > 1 else {'replicable': None, 'runs': len(output_paths)}

    report = {
        'status': 'ok' if all_ok else 'error',
        'process': args.process,
        'repeat_requested': args.repeat,
        'replicability': replicability,
        'runs': [r.__dict__ for r in run_results],
        'output_dir': str(out_dir),
    }

    report_path = out_dir / 'orchestrator_report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    print(json.dumps({'status': report['status'], 'report': str(report_path), 'replicable': replicability.get('replicable')}))
    return 0 if report['status'] == 'ok' else 1


if __name__ == '__main__':
    raise SystemExit(main())
