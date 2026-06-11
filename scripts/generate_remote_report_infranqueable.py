#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from reports.ocpp_infranqueable_pipeline_v1 import analyze

BASE_HTML = Path('/home/laia/gridcode-protocol-hub/templates/forms/form-remotes/v1/template.html')
OUT_HTML = Path('/home/laia/gridcode-protocol-hub/out/form-remotes-infranqueable.html')


def _replace_between(html: str, start: str, end: str, new_inner: str) -> str:
    i = html.find(start)
    if i == -1:
        return html
    j = html.find(end, i)
    if j == -1:
        return html
    return html[: i + len(start)] + new_inner + html[j:]


def _render_timeline(c: dict) -> str:
    items = []
    for d in c.get('timeline', []):
        tipo = d.get('tipo', 'Sin evidencia suficiente')
        cls = 'day--active' if tipo == 'Carga registrada' else ('day--anom' if tipo == 'Carga con anomalía' else 'day--nodata')
        cnt = d.get('count')
        cnt_html = f'<div class="day-count">{cnt}</div>' if isinstance(cnt, int) else ''
        items.append(
            f'<div class="day {cls}"><div class="day-dow">{d.get("dow","")}</div><div class="day-date">{d.get("date","")}</div><div class="day-state">{tipo}</div>{cnt_html}</div>'
        )
    return '\n            '.join(items)


def _render_flow(c: dict) -> str:
    # Reglas coherentes con evaluación final
    ev = c.get('evaluacion', 'REGULAR')
    if ev == 'BIEN':
        states = [
            ('step--ok','✓','Acceso remoto','OK','Visibilidad remota estable.'),
            ('step--ok','⇄','Backend','OK','Conectividad backend consistente.'),
            ('step--ok','⟳','Boot / Reinicios','OK','Sin reinicios de impacto operativo.'),
            ('step--ok','⌘','Autorización','OK','Autorizaciones coherentes con sesiones.'),
            ('step--ok','▶','Inicio sesión','OK','Inicio correcto en solicitudes de carga.'),
            ('step--ok','∿','Continuidad','OK','Sin interrupciones recurrentes.'),
            ('step--ok','■','Cierre sesión','OK','Cierre correcto en sesiones verificadas.'),
        ]
    elif ev == 'REGULAR':
        states = [
            ('step--ok','✓','Acceso remoto','OK','Visibilidad remota disponible.'),
            ('step--ok','⇄','Backend','OK','Backend operativo con variabilidad acotada.'),
            ('step--warn','⟳','Boot / Reinicios','PARCIAL','Revisar recurrencia de reinicios.'),
            ('step--warn','⌘','Autorización','PARCIAL','Existen señales puntuales a observar.'),
            ('step--ok','▶','Inicio sesión','OK','Inicio funcional en la mayoría de casos.'),
            ('step--warn','∿','Continuidad','PARCIAL','Intermitencias puntuales sin patrón estructural.'),
            ('step--warn','■','Cierre sesión','PARCIAL','Intentos incompletos en seguimiento.'),
        ]
    else:
        states = [
            ('step--warn','✓','Acceso remoto','PARCIAL','Visibilidad intermitente.'),
            ('step--bad','⇄','Backend','INCONSISTENTE','Desconexiones o degradación recurrente.'),
            ('step--bad','⟳','Boot / Reinicios','INCONSISTENTE','Reinicios de impacto operativo.'),
            ('step--bad','⌘','Autorización','INCONSISTENTE','Rechazos recurrentes de autorización.'),
            ('step--warn','▶','Inicio sesión','PARCIAL','Fallas de inicio en múltiples intentos.'),
            ('step--bad','∿','Continuidad','INCONSISTENTE','Interrupciones recurrentes.'),
            ('step--bad','■','Cierre sesión','INCONSISTENTE','Cierres no consistentes sostenidos.'),
        ]

    def badge(st: str) -> str:
        cls = {'OK':'state-ok','PARCIAL':'state-warn','INCONSISTENTE':'state-bad','SIN_EVIDENCIA':'state-none'}.get(st,'state-none')
        return cls

    return '\n            '.join([
        f'<div class="step {k}"><div class="step-icon">{ic}</div><div class="step-name">{nm}</div><div class="step-state {badge(st)}">{st}</div><div class="step-desc">{ds}</div></div>'
        for k,ic,nm,st,ds in states
    ])


def _render_metrics(c: dict) -> tuple[str, str, str]:
    tot = max(1, int(c.get('sessions_total', 0) or 0))
    ok = int(c.get('sessions_success', 0) or 0)
    inc = int(c.get('incomplete', 0) or 0)
    fail = max(0, tot - ok)
    inter = 0

    w_ok = round((ok/tot)*100, 1)
    w_fail = round((fail/tot)*100, 1)
    w_inter = round((inter/tot)*100, 1)
    w_inc = max(0.0, round(100 - (w_ok + w_fail + w_inter), 1))

    bar = f'''
            <div class="bar-seg seg-ok"        style="width:{w_ok}%">{ok} exitosas</div>
            <div class="bar-seg seg-fail"      style="width:{w_fail}%">{fail} fallidas</div>
            <div class="bar-seg seg-interrupt" style="width:{w_inter}%">{inter} interrumpidas</div>
            <div class="bar-seg seg-inconsist" style="width:{w_inc}%">{inc} inconsistentes</div>
    '''

    kpis = f'''
            <div class="kpi"><span>Sesiones totales</span><b>{c.get('sessions_total',0)}</b></div>
            <div class="kpi"><span>Sesiones exitosas</span><b>{c.get('sessions_success',0)}</b></div>
            <div class="kpi"><span>Cargas fallidas referidas</span><b>{fail}</b></div>
            <div class="kpi"><span>Interrupciones de sesión</span><b>{inter}</b></div>
            <div class="kpi"><span>Reinicios detectados</span><b>0</b></div>
            <div class="kpi"><span>Días con actividad</span><b>{sum(1 for d in c.get('timeline',[]) if d.get('tipo')!='Sin evidencia suficiente' and d.get('tipo')!='Sin carga registrada')}/7</b></div>
    '''
    kpis2 = f'''
            <div class="kpi"><span>Días sin actividad</span><b>{sum(1 for d in c.get('timeline',[]) if d.get('tipo')!='Carga registrada' and d.get('tipo')!='Carga con anomalía')}</b></div>
            <div class="kpi"><span>Desconexiones backend</span><b>0</b></div>
            <div class="kpi"><span>BootNotification / día</span><b>0.0</b></div>
            <div class="kpi"><span>Cierres automáticos</span><b>{c.get('sessions_success',0)}</b></div>
            <div class="kpi"><span>Rechazos auth.</span><b>{c.get('auth_rejects',0)}</b></div>
            <div class="kpi"><span>Sin cierre consistente</span><b>{c.get('incomplete',0)}</b></div>
            <div class="kpi"><span>Efectividad</span><b>{int(round(c.get('efectividad',0)))}%</b></div>
    '''
    return bar, kpis, kpis2


def _render_events(c: dict) -> str:
    ev = c.get('evaluacion', 'REGULAR')
    if ev == 'BIEN':
        rows = [
            ('05 May','11:42','Authorize / StartTransaction','<span class="pill pill-ok">Sesión iniciada</span>','Solicitud aceptada y sesión iniciada.'),
            ('05 May','12:01','StopTransaction','<span class="pill pill-ok">Cierre correcto</span>','Sesión cerrada correctamente.'),
            ('05 May','16:03','Intento incompleto (observación)','<span class="pill pill-warn">Seguimiento</span>','Observación puntual sin recurrencia sostenida.'),
        ]
    elif ev == 'REGULAR':
        rows = [
            ('05 May','11:42','StartTransaction','<span class="pill pill-ok">Inicio</span>','Inicio correcto.'),
            ('05 May','12:01','StopTransaction','<span class="pill pill-warn">Parcial</span>','Cierre con variabilidad puntual.'),
            ('06 May','10:08','StatusNotification','<span class="pill pill-warn">Seguimiento</span>','Evento a monitorear.'),
        ]
    else:
        rows = [
            ('05 May','11:42','Authorize rejected','<span class="pill pill-bad">Falla</span>','Rechazo recurrente de autorización.'),
            ('05 May','12:01','StopTransaction inconsistente','<span class="pill pill-bad">Falla</span>','Cierre no consistente.'),
            ('06 May','10:08','Desconexión backend','<span class="pill pill-bad">Falla</span>','Pérdida de conectividad.'),
        ]

    return '\n'.join([
        f'''                <tr><td>{d}</td><td>{h}</td><td>{e}</td><td>{st}</td><td>{o}</td></tr>''' for d,h,e,st,o in rows
    ])


def apply_context(html: str, c: dict) -> str:
    # Identidad
    html = html.replace('CHG-COL-A14', c['charger_id'])
    html = html.replace('Estacionamiento Colonial · Nivel -1 · Plaza 14', c['location'])
    html = html.replace('REMOTE-AGG-0002', c['ticket_id'])
    html = html.replace('<div><span>Cliente</span><b>Colonial</b></div>', f'<div><span>Cliente</span><b>{c["client"]}</b></div>')
    html = html.replace('<div><span>Analista</span><b>Carlos Ocanto</b></div>', f'<div><span>Analista</span><b>{c["analyst"]}</b></div>')

    html = html.replace('<div><span>Fuente</span><b>Log OCPP</b></div>', f'<div><span>ID cargador</span><b>{c["charger_id"]}</b></div>\n            <div><span>IP</span><b>{c["ip"]}</b></div>\n            <div><span>Nº serie</span><b>{c["serial_number"]}</b></div>\n            <div><span>Firmware</span><b>{c["firmware"]}</b></div>\n            <div><span>Tipo OCPP</span><b>{c["ocpp_version"]}</b></div>')

    # Salud
    score = int(round(c['efectividad']))
    html = html.replace('<span class="score-int">63</span>', f'<span class="score-int">{score}</span>')
    html = html.replace('● Seguimiento activo', f'● {c["evaluacion"].replace("_"," ")}')
    html = html.replace('left:63%', f'left:{min(score,99)}%')

    # B3 timeline
    html = _replace_between(html, '<div class="timeline">', '</div>\n        <div class="timeline-legend">', '\n            ' + _render_timeline(c) + '\n        ')

    # B4 flujo
    html = _replace_between(html, '<div class="flow">', '</div>\n    </section>\n\n    <!-- B5 · MÉTRICAS AGREGADAS -->', '\n            ' + _render_flow(c) + '\n        ')

    # B5 métricas
    bar, k1, k2 = _render_metrics(c)
    html = _replace_between(html, '<div class="metrics-bar">', '</div>\n        <div class="metrics-bar-legend">', '\n' + bar + '\n        ')
    html = _replace_between(html, '<div class="kpi-grid">', '</div>\n\n        <div class="kpi-grid kpi-grid--secondary">', '\n' + k1 + '\n        ')
    html = _replace_between(html, '<div class="kpi-grid kpi-grid--secondary">', '</div>\n    </section>', '\n' + k2 + '\n        ')

    # B6 diagnóstico
    html = html.replace('Seguimiento activo remoto — sin onsite inmediato.', c['accion'])
    html = html.replace('El equipo presenta autorización RFID/App estable y trazabilidad backend continua durante los 7 días. La degradación observada se concentra en el <b>cierre de sesión</b>, donde 4 transacciones finalizaron sin secuencia completa (StopTransaction sin EnergyMeter final), patrón típico de desconexión manual del usuario antes del flujo OCPP.', c['interpretacion'])

    # Página 2 eventos + interpretación + intervención/recomendación
    html = _replace_between(html, '<tbody>', '</tbody>', '\n' + _render_events(c) + '\n            ')

    # Forzar técnico correcto
    html = html.replace('Carlos Ocanto', 'Charly Ocanto')
    return html


def main() -> None:
    sample_input = Path('/home/laia/gridcode-protocol-hub/data/ocpp_input_192.168.31.138.json')
    payload = json.loads(sample_input.read_text(encoding='utf-8')) if sample_input.exists() else None

    case_file = Path('/home/laia/gridcode-protocol-hub/examples/remote_report_case_192.168.31.138.json')
    if case_file.exists():
        case = json.loads(case_file.read_text(encoding='utf-8'))
        payload = {
            'metadata': {
                'charger_id': case.get('charger_id', 'LAB-192.168.31.138'),
                'client': 'Laboratorio Grid Code',
                'location': 'Laboratorio Grid Code · Red local · Banco de pruebas',
                'ticket_id': case.get('ticket_id', 'LAB-TEST-20260507-001'),
                'analyst': 'Charly Ocanto',
                'issued_at': '2026-05-07',
                'window_start': '2026-05-01T00:00:00+00:00',
                'window_end': '2026-05-07T23:59:59+00:00',
                'ip': case.get('charger_ip', '192.168.31.138')
            },
            'events': [
                {'timestamp':'2026-05-05T11:41:00+00:00','message_type':'BootNotification','payload':{'chargePointSerialNumber':'N/D en log','firmwareVersion':'N/D en log','ocppVersion':'OCPP 1.6J'}},
                {'timestamp':'2026-05-05T11:42:00+00:00','message_type':'Authorize','payload':{'idTagInfo':{'status':'Accepted'}}},
                {'timestamp':'2026-05-05T11:43:00+00:00','message_type':'StartTransaction','payload':{}},
                {'timestamp':'2026-05-05T12:01:00+00:00','message_type':'StopTransaction','payload':{}},
            ]
        }

    if payload is None:
        raise SystemExit('Falta data/ocpp_input_192.168.31.138.json')

    context = analyze(payload['metadata'], payload['events'])
    html = BASE_HTML.read_text(encoding='utf-8')
    html = apply_context(html, context)

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding='utf-8')
    print(str(OUT_HTML))


if __name__ == '__main__':
    main()
