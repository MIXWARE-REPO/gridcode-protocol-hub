#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from shared.orchestration.cpms_playwright_v1 import (
    CpmsRunConfig,
    run_cpms_playwright_session,
    save_cpms_run_json,
)

ROOT = Path('/home/laia/gridcode-protocol-hub')
DEFAULT_OUT = ROOT / 'out' / 'cpms-playwright'
VERSION = 'cpms_playwright_protocol_v1'


@dataclass
class InputData:
    run_id: str
    base_url: str
    username: str
    password: str
    headless: bool = True
    create_charger: bool = False
    charger_id: str | None = None
    charger_name: str | None = None
    connector_count: int = 1
    create_user: bool = False
    user_full_name: str | None = None
    user_username: str | None = None
    user_password: str | None = None
    user_tag_id: str | None = None
    user_company: str | None = None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Protocolo CPMS separado (Playwright)')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--out-base', default=str(DEFAULT_OUT))
    return p.parse_args()


def load_input(path: Path) -> InputData:
    raw = json.loads(path.read_text(encoding='utf-8'))
    for k in ['run_id', 'base_url', 'username', 'password']:
        if k not in raw:
            raise ValueError(f'missing_required_field:{k}')
    return InputData(**raw)


def main() -> int:
    args = parse_args()
    inp = load_input(Path(args.input))

    out_dir = Path(args.out_base) / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{inp.run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = CpmsRunConfig(
        base_url=inp.base_url,
        username=inp.username,
        password=inp.password,
        create_charger=inp.create_charger,
        charger_id=inp.charger_id,
        charger_name=inp.charger_name,
        connector_count=inp.connector_count,
        create_user=inp.create_user,
        user_full_name=inp.user_full_name,
        user_username=inp.user_username,
        user_password=inp.user_password,
        user_tag_id=inp.user_tag_id,
        user_company=inp.user_company,
        headless=inp.headless,
    )

    result = run_cpms_playwright_session(cfg, out_dir=out_dir)
    cpms_json = save_cpms_run_json(result, out_dir / '01_cpms_result.json')

    summary = {
        'version': VERSION,
        'status': 'ok' if result.get('ok') else 'error',
        'run_id': inp.run_id,
        'artifacts': {
            'run_dir': str(out_dir),
            'cpms_result_json': str(cpms_json),
        },
        'actions': result.get('actions', []),
        'warnings': result.get('warnings', []),
        'errors': result.get('errors', []),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': summary['status'], 'output': str(out_path)}, ensure_ascii=False))
    return 0 if summary['status'] == 'ok' else 1


if __name__ == '__main__':
    raise SystemExit(main())
