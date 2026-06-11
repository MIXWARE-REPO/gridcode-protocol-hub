#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

VERSION = 'nubas_monitoring_protocol_v1'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Protocolo base de integración Nubas Monitoring (v1)')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    raw = json.loads(Path(args.input).read_text(encoding='utf-8'))

    # Placeholder contractual: base para completar cuando terminen de enseñar el flujo Nubas.
    out = {
        'version': VERSION,
        'status': 'ok',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'message': 'Base protocol ready. Pending Nubas UI operational steps mapping.',
        'input_echo': {
            'run_id': raw.get('run_id'),
            'base_url': raw.get('base_url'),
            'scope': raw.get('scope', 'monitoring'),
        },
        'next_required': [
            'login_selectors',
            'target_tabs',
            'metrics_to_extract',
            'alerts_and_thresholds',
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'ok', 'output': str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
