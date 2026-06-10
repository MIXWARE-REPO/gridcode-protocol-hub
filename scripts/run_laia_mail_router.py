#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.orchestration.laia_mail_router_v1 import run_laia_mail_router


def main() -> int:
    ap = argparse.ArgumentParser(description='Run Laia Mail Router from JSON input.')
    ap.add_argument('--input', required=True, help='Path to the JSON payload for the router.')
    ap.add_argument('--output', required=True, help='Path where the router output JSON will be written.')
    args = ap.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    payload = json.loads(input_path.read_text(encoding='utf-8'))
    result = run_laia_mail_router(payload)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'ok', 'output': str(output_path)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
