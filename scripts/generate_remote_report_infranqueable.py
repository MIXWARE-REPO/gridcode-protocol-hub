#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from reports.ocpp_infranqueable_pipeline_v1 import analyze

BASE_HTML = Path('/home/laia/gridcode-protocol-hub/templates/forms/form-remotes/v1/template.html')
OUT_HTML = Path('/home/laia/gridcode-protocol-hub/out/form-remotes-infranqueable.html')


def apply_context(html: str, c: dict) -> str:
    # Identidad
    html = html.replace('CHG-COL-A14', c['charger_id'])
    html = html.replace('Estacionamiento Colonial · Nivel -1 · Plaza 14', c['location'])
    html = html.replace('REMOTE-AGG-0002', c['ticket_id'])
    html = html.replace('<div><span>Cliente</span><b>Colonial</b></div>', f'<div><span>Cliente</span><b>{c["client"]}</b></div>')
    html = html.replace('<div><span>Analista</span><b>Carlos Ocanto</b></div>', f'<div><span>Analista</span><b>{c["analyst"]}</b></div>')

    # Meta extendida in-frame
    html = html.replace('<div><span>Fuente</span><b>Log OCPP</b></div>', f'<div><span>ID cargador</span><b>{c["charger_id"]}</b></div>\n            <div><span>IP</span><b>{c["ip"]}</b></div>\n            <div><span>Nº serie</span><b>{c["serial_number"]}</b></div>\n            <div><span>Firmware</span><b>{c["firmware"]}</b></div>\n            <div><span>Tipo OCPP</span><b>{c["ocpp_version"]}</b></div>')

    # Salud
    score = int(round(c['efectividad']))
    html = html.replace('<span class="score-int">63</span>', f'<span class="score-int">{score}</span>')
    html = html.replace('● Seguimiento activo', f'● {c["evaluacion"].title().replace("_", " ")}')
    html = html.replace('left:63%', f'left:{min(score,99)}%')

    # Diagnóstico
    html = html.replace('Seguimiento activo remoto — sin onsite inmediato.', c['accion'])
    html = html.replace('El equipo presenta autorización RFID/App estable y trazabilidad backend continua durante los 7 días. La degradación observada se concentra en el <b>cierre de sesión</b>, donde 4 transacciones finalizaron sin secuencia completa (StopTransaction sin EnergyMeter final), patrón típico de desconexión manual del usuario antes del flujo OCPP.', c['interpretacion'])

    # Forzar técnico correcto
    html = html.replace('Carlos Ocanto', 'Charly Ocanto')

    return html


def main() -> None:
    sample_input = Path('/home/laia/gridcode-protocol-hub/data/ocpp_input_192.168.31.138.json')
    if not sample_input.exists():
        sample_input.parent.mkdir(parents=True, exist_ok=True)
        sample_input.write_text(json.dumps({
            'metadata': {
                'charger_id': 'LAB-192.168.31.138',
                'client': 'Laboratorio Grid Code',
                'location': 'Laboratorio Grid Code · Red local · Banco de pruebas',
                'ticket_id': 'LAB-TEST-20260507-001',
                'analyst': 'Charly Ocanto',
                'issued_at': '2026-05-07',
                'window_start': '2026-05-01T00:00:00+00:00',
                'window_end': '2026-05-07T23:59:59+00:00',
                'ip': '192.168.31.138'
            },
            'events': [
                {'timestamp':'2026-05-05T11:41:00+00:00','message_type':'BootNotification','payload':{'chargePointSerialNumber':'WB-138-XYZ','firmwareVersion':'1.2.3','ocppVersion':'OCPP 1.6J'}},
                {'timestamp':'2026-05-05T11:42:00+00:00','message_type':'Authorize','payload':{'idTagInfo':{'status':'Accepted'}}},
                {'timestamp':'2026-05-05T11:43:00+00:00','message_type':'StartTransaction','payload':{}},
                {'timestamp':'2026-05-05T12:01:00+00:00','message_type':'StopTransaction','payload':{}},
            ]
        }, ensure_ascii=False, indent=2), encoding='utf-8')

    payload = json.loads(sample_input.read_text(encoding='utf-8'))
    context = analyze(payload['metadata'], payload['events'])

    html = BASE_HTML.read_text(encoding='utf-8')
    html = apply_context(html, context)

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding='utf-8')
    print(str(OUT_HTML))


if __name__ == '__main__':
    main()
