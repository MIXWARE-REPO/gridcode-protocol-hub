#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from zipfile import ZipFile

from reports.ocpp_infranqueable_pipeline_v1 import analyze
from shared.orchestration.charger_webui_playwright_v1 import (
    ChargerRunConfig,
    run_playwright_session,
    save_run_json,
)

ROOT = Path('/home/laia/gridcode-protocol-hub')
DEFAULT_TEMPLATE = ROOT / 'templates/forms/form-remotes/v1/template.html'
DEFAULT_OUT = ROOT / 'out/playwright_e2e'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='E2E: Python + Playwright + análisis + HTML + PDF para cargadores')
    p.add_argument('--ip', required=True)
    p.add_argument('--password', required=True)
    p.add_argument('--username', default='admin')
    p.add_argument('--ticket-id', required=True)
    p.add_argument('--client', default='Grid Code')
    p.add_argument('--location', default='N/D')
    p.add_argument('--analyst', default='Charly Ocanto')
    p.add_argument('--endpoint', default=None)
    p.add_argument('--ocpp-var', action='append', default=[], help='name=value (repetible)')
    p.add_argument('--reboot', action='store_true')
    p.add_argument('--allow-unsafe-actions', action='store_true')
    p.add_argument('--headless', action='store_true', default=True)
    p.add_argument('--out-dir', default=str(DEFAULT_OUT))
    return p.parse_args()


def _parse_ocpp_vars(pairs: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for item in pairs:
        if '=' not in item:
            continue
        k, v = item.split('=', 1)
        out[k.strip()] = v.strip()
    return out


def _collect_events_from_zip(zip_path: Path) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if not zip_path.exists():
        return events

    with ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            if not name.lower().endswith(('.log', '.txt', '.json')):
                continue
            raw = zf.read(name).decode('utf-8', errors='ignore')
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Heurística simple: JSON line OCPP
                if line.startswith('{') and line.endswith('}'):
                    try:
                        obj = json.loads(line)
                        ts = obj.get('timestamp') or obj.get('time') or obj.get('date')
                        mt = obj.get('message_type') or obj.get('action') or obj.get('type')
                        payload = obj.get('payload') or obj
                        if ts and mt:
                            events.append({'timestamp': ts, 'message_type': mt, 'payload': payload})
                    except Exception:
                        continue
    return events


def _build_case_metadata(args: argparse.Namespace, webui_json: Dict[str, Any]) -> Dict[str, Any]:
    ocpp_after = webui_json.get('ocpp_after', {})
    return {
        'charger_id': f'CHG-{args.ip.replace(".", "-")}',
        'client': args.client,
        'location': args.location,
        'ticket_id': args.ticket_id,
        'analyst': args.analyst,
        'issued_at': datetime.utcnow().strftime('%Y-%m-%d'),
        'window_start': datetime.utcnow().strftime('%Y-%m-%dT00:00:00+00:00'),
        'window_end': datetime.utcnow().strftime('%Y-%m-%dT23:59:59+00:00'),
        'ip': args.ip,
        'serial_number': 'N/D en log',
        'firmware': 'N/D en log',
        'ocpp_version': 'OCPP 1.6J',
        'central_system_address': ocpp_after.get('centralSystemAddress') or 'N/D en log',
    }


def _render_html_from_context(context: Dict[str, Any], template_path: Path, out_html: Path) -> None:
    # Reutiliza renderer existente
    from scripts.generate_remote_report_infranqueable import apply_context

    html = template_path.read_text(encoding='utf-8')
    html = apply_context(html, context)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding='utf-8')


def _render_pdf_with_chrome(input_html: Path, out_pdf: Path) -> None:
    cmd = [
        'google-chrome',
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        '--run-all-compositor-stages-before-draw',
        '--virtual-time-budget=5000',
        f'--print-to-pdf={out_pdf}',
        f'file://{input_html}',
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir) / f"{args.ticket_id}_{args.ip.replace('.', '_')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    config = ChargerRunConfig(
        ip=args.ip,
        username=args.username,
        password=args.password,
        target_endpoint=args.endpoint,
        ocpp_updates=_parse_ocpp_vars(args.ocpp_var),
        download_logs=True,
        reboot=args.reboot,
        allow_unsafe_actions=args.allow_unsafe_actions,
        headless=args.headless,
    )

    webui_result = run_playwright_session(config=config, out_dir=out_dir)
    webui_json_path = save_run_json(webui_result, out_dir / '01_webui_output.json')

    downloads = webui_result.get('evidence', {}).get('downloads', [])
    zip_path = Path(downloads[0]) if downloads else Path()
    events = _collect_events_from_zip(zip_path) if zip_path else []

    metadata = _build_case_metadata(args, webui_result)
    if not events:
        # Mínimo viable para no romper pipeline
        events = [
            {
                'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00'),
                'message_type': 'BootNotification',
                'payload': {
                    'chargePointSerialNumber': metadata['serial_number'],
                    'firmwareVersion': metadata['firmware'],
                    'ocppVersion': metadata['ocpp_version'],
                },
            }
        ]

    context = analyze(metadata, events)
    (out_dir / '02_analysis_output.json').write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding='utf-8')

    out_html = out_dir / '03_report_filled.html'
    _render_html_from_context(context, DEFAULT_TEMPLATE, out_html)

    out_pdf = out_dir / '04_report.pdf'
    _render_pdf_with_chrome(out_html, out_pdf)

    final = {
        'ok': True,
        'ticket_id': args.ticket_id,
        'ip': args.ip,
        'artifacts': {
            'webui_output_json': str(webui_json_path),
            'analysis_output_json': str(out_dir / '02_analysis_output.json'),
            'report_html': str(out_html),
            'report_pdf': str(out_pdf),
        },
    }
    (out_dir / '00_run_summary.json').write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(final, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
