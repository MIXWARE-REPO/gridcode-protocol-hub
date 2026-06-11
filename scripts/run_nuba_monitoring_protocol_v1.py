#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

VERSION = 'nuba_monitoring_protocol_v1'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Protocolo NUBA Monitoring v1 (base operativa)')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    raw = json.loads(Path(args.input).read_text(encoding='utf-8'))

    out = {
        'version': VERSION,
        'status': 'ok',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'platform': 'NUBA',
        'scope': 'cloud multi-instance monitoring/control/management',
        'input_echo': {
            'run_id': raw.get('run_id'),
            'base_url': raw.get('base_url', 'https://nuba.grid.touch'),
            'operator_role': raw.get('operator_role', 'super_admin'),
            'target_creator': raw.get('target_creator'),
        },
        'checklist': [
            'login',
            'open_administration',
            'filter_by_creator',
            'inspect_clusters_and_nodes',
            'inspect_sessions_and_backups',
            'inspect_connections_energy_system_settings',
            'if_teleport_active_open_teleport_support',
            'verify_dashboard_active_state'
        ],
        'note': 'Protocol skeleton upgraded with real NUBA domain concepts. Pending Playwright selector mapping during live UI walkthrough.'
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'ok', 'output': str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
