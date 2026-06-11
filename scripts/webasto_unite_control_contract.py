#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path('/home/laia/gridcode-protocol-hub')
SUPABASE_SCHEMA = 'website/docs/reference/supabase-charger-registry-schema.sql'
RUNBOOK = 'docs/runbook-colonial-ocpp-webasto-unite-v1.md'
CONTRACT_MD = 'docs/webasto-unite-control-contract.md'
VPN_SKILL = 'productivity/colonial-vpn-charger-access/SKILL.md'
STRICT_RUNNER = 'scripts/webasto_unite_strict_playwright.py'
UNIFIED_RUNNER = 'scripts/webasto_unite_cpms_unified_playwright_v2.py'

ACTION_PROFILES: Dict[str, Dict[str, Any]] = {
    'change_id': {
        'label': 'Cambio de ID',
        'runner': STRICT_RUNNER,
        'runner_mode': 'playwright',
        'expected': [
            'guardar cambio',
            'reentrar a la pantalla',
            'confirmar persistencia del ID',
        ],
        'artifacts': ['html_before', 'html_after', 'screenshot_final'],
    },
    'change_ocpp_endpoint': {
        'label': 'Cambio de endpoint OCPP',
        'runner': STRICT_RUNNER,
        'runner_mode': 'playwright',
        'expected': [
            'guardar Central System Address',
            'reabrir OCPP Settings',
            'verificar endpoint persistido',
        ],
        'artifacts': ['html_before', 'html_after', 'screenshot_final'],
    },
    'download_event_log': {
        'label': 'Descarga de log de eventos',
        'runner': STRICT_RUNNER,
        'runner_mode': 'playwright',
        'expected': [
            'navegar a System / System Maintenance',
            'disparar descarga de ZIP',
            'esperar a que el archivo aparezca en evidencias',
        ],
        'artifacts': ['download_zip', 'screenshot_final'],
    },
    'firmware_update': {
        'label': 'Actualización de firmware',
        'runner': None,
        'runner_mode': 'blocked',
        'expected': [
            'no ejecutar con runners de ID/OCPP/logs',
            'esperar runner dedicado validado',
        ],
        'artifacts': [],
    },
}

ACTION_ALIASES = {
    'id': 'change_id',
    'change_id': 'change_id',
    'set_id': 'change_id',
    'ocpp': 'change_ocpp_endpoint',
    'endpoint': 'change_ocpp_endpoint',
    'change_ocpp_endpoint': 'change_ocpp_endpoint',
    'log': 'download_event_log',
    'logs': 'download_event_log',
    'download_event_log': 'download_event_log',
    'firmware': 'firmware_update',
    'fw': 'firmware_update',
    'firmware_update': 'firmware_update',
}

@dataclass
class IdentityCheck:
    provided_fields: List[str]
    rule: str
    status: str
    notes: List[str]


def _load_json(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _normalize_ip(ip: str | None) -> str:
    return (ip or '').strip()


def classify_network(ip: str | None) -> Dict[str, str]:
    ip = _normalize_ip(ip)
    if ip.startswith('10.'):
        return {
            'classification': 'colonial',
            'access_mode': 'vpn',
            'reason': 'IP 10.x.x.x pertenece a COLONIAL y requiere VPN',
        }
    if ip.startswith('192.168.31.'):
        return {
            'classification': 'lab',
            'access_mode': 'direct',
            'reason': 'IP 192.168.31.x pertenece al laboratorio y se accede por LAN',
        }
    if ip:
        return {
            'classification': 'unknown',
            'access_mode': 'blocked',
            'reason': 'IP no clasificada por regla documental',
        }
    return {
        'classification': 'missing',
        'access_mode': 'blocked',
        'reason': 'Falta IP para clasificar la red',
    }


def identity_status(payload: Dict[str, Any]) -> IdentityCheck:
    fields = []
    for key in ('charger_ip', 'plaza', 'serie', 'id_colonial'):
        if payload.get(key):
            fields.append(key)

    rule = '1 dato = verificar; 2 datos = confrontar'
    notes: List[str] = []
    if not fields:
        return IdentityCheck(fields, rule, 'blocked', ['Falta identidad mínima del cargador'])

    if len(fields) == 1:
        notes.append(f'Verificar único dato: {fields[0]}')
        return IdentityCheck(fields, rule, 'verify', notes)

    notes.append('Confrontar datos disponibles y exigir coincidencia')
    return IdentityCheck(fields, rule, 'confront', notes)


def pick_action(action_raw: str | None) -> str:
    key = (action_raw or '').strip().lower()
    return ACTION_ALIASES.get(key, key)


def build_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    action_key = pick_action(payload.get('action'))
    profile = ACTION_PROFILES.get(action_key)
    identity = identity_status(payload)
    network = classify_network(payload.get('charger_ip'))

    blocked: List[str] = []
    if identity.status == 'blocked':
        blocked.append('missing_identity')
    if network['access_mode'] == 'blocked':
        blocked.append('missing_or_unclassified_ip')
    if not profile:
        blocked.append('unknown_action')

    if network['classification'] == 'colonial' and network['access_mode'] != 'blocked':
        connection_skill = VPN_SKILL
    elif network['classification'] == 'lab':
        connection_skill = None
    else:
        connection_skill = None

    connection_path = 'vpn' if network['classification'] == 'colonial' else 'direct' if network['classification'] == 'lab' else 'blocked'

    action_blocked = action_key == 'firmware_update' or profile is None
    if action_blocked and action_key == 'firmware_update':
        blocked.append('firmware_update_out_of_happy_path')

    decision = 'blocked' if blocked else 'ready'

    expected_prechecks = [
        f'Leer {SUPABASE_SCHEMA}',
        f'Consultar {RUNBOOK}',
        'Identificar cargador con 1 dato=verificar / 2 datos=confrontar',
        'Clasificar red por IP antes de tocar UI',
    ]

    if connection_path == 'vpn':
        expected_prechecks.append(f'Usar {VPN_SKILL} para conectar a COLONIAL')
    elif connection_path == 'direct':
        expected_prechecks.append('Conexión directa por LAN de laboratorio')
    else:
        expected_prechecks.append('Conexión bloqueada hasta clasificar IP')

    action_plan: Dict[str, Any] = {
        'requested_action': payload.get('action'),
        'normalized_action': action_key,
        'label': profile['label'] if profile else None,
        'runner': profile['runner'] if profile else None,
        'runner_mode': profile['runner_mode'] if profile else 'unknown',
        'expected': profile['expected'] if profile else [],
        'artifacts': profile['artifacts'] if profile else [],
    }

    result = {
        'status': decision,
        'source_of_truth': {
            'supabase_schema': SUPABASE_SCHEMA,
            'runbook': RUNBOOK,
            'control_contract': CONTRACT_MD,
            'vpn_skill': VPN_SKILL,
        },
        'identity': asdict(identity),
        'network': network,
        'connection': {
            'mode': connection_path,
            'skill': connection_skill,
        },
        'action': action_plan,
        'prechecks': expected_prechecks,
        'blockers': blocked,
        'paths': {
            'strict_runner': STRICT_RUNNER,
            'unified_runner': UNIFIED_RUNNER,
        },
        'what_to_do_next': [],
        'what_to_expect': [],
    }

    if decision == 'blocked':
        if 'missing_identity' in blocked:
            result['what_to_do_next'].append('Completar identidad del cargador con plaza/serie/ID Colonial/IP')
        if 'missing_or_unclassified_ip' in blocked:
            result['what_to_do_next'].append('Aportar IP para decidir si es COLONIAL o laboratorio')
        if 'unknown_action' in blocked:
            result['what_to_do_next'].append('Definir acción concreta: change_id, change_ocpp_endpoint, download_event_log o firmware_update')
        if 'firmware_update_out_of_happy_path' in blocked:
            result['what_to_do_next'].append('Esperar runner dedicado de firmware antes de ejecutar')
    else:
        result['what_to_do_next'] = [
            'Resolver red y conectividad según clasificación',
            'Ejecutar runner Playwright correspondiente',
            'Verificar persistencia o descarga real',
            'Guardar evidencia y cerrar con resultado contractual',
        ]
        result['what_to_expect'] = profile['expected'] if profile else []

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Contrato determinista de control Webasto/Unite')
    parser.add_argument('--input', help='JSON de entrada con charger_ip/plaza/serie/id_colonial/action')
    parser.add_argument('--output', help='Archivo JSON de salida')
    args = parser.parse_args()

    payload = _load_json(args.input)
    plan = build_plan(payload)

    text = json.dumps(plan, indent=2, ensure_ascii=False)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding='utf-8')
    print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
