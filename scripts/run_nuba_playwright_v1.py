#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from shared.orchestration.nuba_playwright_v1 import (
    NubaRunConfig,
    run_nuba_playwright_session,
    save_nuba_run_json,
)

ROOT = Path('/home/laia/gridcode-protocol-hub')
DEFAULT_OUT = ROOT / 'out' / 'nuba-playwright'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='NUBA Playwright protocol v1')
    p.add_argument('--base-url', default='https://nuba.grid.touch')
    p.add_argument('--username', required=True)
    p.add_argument('--password', required=True)
    p.add_argument('--creator-filter', default=None)
    p.add_argument('--open-teleport', action='store_true')
    p.add_argument('--create-activation-code', action='store_true')
    p.add_argument('--activation-description', default=None)
    p.add_argument('--activation-product', default=None)
    p.add_argument('--activation-modules-csv', default=None)
    p.add_argument('--activation-expiry-date', default=None)
    p.add_argument('--headless', action='store_true', default=True)
    p.add_argument('--output', required=True)
    p.add_argument('--out-base', default=str(DEFAULT_OUT))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = Path(args.out_base) / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_nuba"
    run_dir.mkdir(parents=True, exist_ok=True)

    cfg = NubaRunConfig(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
        creator_filter=args.creator_filter,
        open_teleport_if_available=args.open_teleport,
        create_activation_code=args.create_activation_code,
        activation_description=args.activation_description,
        activation_product=args.activation_product,
        activation_modules_csv=args.activation_modules_csv,
        activation_expiry_date=args.activation_expiry_date,
        headless=args.headless,
    )
    result = run_nuba_playwright_session(cfg, out_dir=run_dir)
    raw_json = save_nuba_run_json(result, run_dir / '01_nuba_result.json')

    summary = {
        'status': 'ok' if result.get('ok') else 'error',
        'artifacts': {
            'run_dir': str(run_dir),
            'raw_result': str(raw_json),
        },
        'actions': result.get('actions', []),
        'warnings': result.get('warnings', []),
        'errors': result.get('errors', []),
        'observations': result.get('observations', {}),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': summary['status'], 'output': str(out_path)}, ensure_ascii=False))
    return 0 if summary['status'] == 'ok' else 1


if __name__ == '__main__':
    raise SystemExit(main())
