#!/usr/bin/env python3
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from weasyprint import HTML

TEMPLATE = Path('/home/laia/gridcode-protocol-hub/templates/forms/form-remotes/v1/template.html')
OUT_HTML = Path('/home/laia/gridcode-protocol-hub/out/form-remotes-192.168.31.138-strict.html')
OUT_PDF = Path('/home/laia/gridcode-protocol-hub/out/form-remotes-192.168.31.138-strict.pdf')

DATA = {
    'charger_id': 'LAB-192.168.31.138',
    'ubicacion': 'Laboratorio Grid Code · Red local · Banco de pruebas',
    'ticket': 'LAB-TEST-20260507-001',
    'cliente': 'Laboratorio Grid Code',
    'analista': 'Laia',
    'emision': '2026-05-07',
    'fuente': 'Log OCPP',
    'unidad': 'Cargador individual',
    'window_label': 'Últimos 7 días',
    'window_range': '2026-05-01 → 2026-05-07',
    'efectividad': 100,
    'banda': 'Sano',
    'timeline': [
        {'dow':'Vie','date':'01 May','tipo':'Sin carga registrada','count':None,'reinicio':False,'cierre':False},
        {'dow':'Sáb','date':'02 May','tipo':'Sin carga registrada','count':None,'reinicio':False,'cierre':False},
        {'dow':'Dom','date':'03 May','tipo':'Sin carga registrada','count':None,'reinicio':False,'cierre':False},
        {'dow':'Lun','date':'04 May','tipo':'Sin carga registrada','count':None,'reinicio':False,'cierre':False},
        {'dow':'Mar','date':'05 May','tipo':'Carga registrada','count':1,'reinicio':False,'cierre':False},
        {'dow':'Mié','date':'06 May','tipo':'Sin carga registrada','count':None,'reinicio':False,'cierre':False},
        {'dow':'Jue','date':'07 May','tipo':'Sin carga registrada','count':None,'reinicio':False,'cierre':False},
    ],
    'flow': [
        ('✓','Acceso remoto','OK','Conectividad backend estable durante la ventana.','ok'),
        ('⇄','Backend','OK','Conexión confirmada desde 05/05.','ok'),
        ('⟳','Boot / Reinicios','SIN_EVIDENCIA','Sin reinicios relevantes en la evidencia del período.','nodata'),
        ('⌘','Autorización','OK','Las cargas solicitadas fueron aceptadas operativamente.','ok'),
        ('▶','Inicio sesión','OK','Inicio de sesión correcto cuando se solicitó carga.','ok'),
        ('∿','Continuidad','OK','Sin interrupciones recurrentes en sesiones verificadas.','ok'),
        ('■','Cierre sesión','PARCIAL','Intentos incompletos observados puntualmente, sin recurrencia.','warn'),
    ],
    'metricas': {
        'totales':1,'exitosas':1,'fallidas':0,'interrumpidas':0,'inconsistentes':0,
        'reinicios':0,'dias_actividad':'1/7','dias_sin':6,'boot_dia':'0.0','cierres_auto':1,'rechazos':0,'sin_cierre':0
    },
}


def section_replace(html: str, start_marker: str, end_marker: str, new_content: str) -> str:
    i = html.find(start_marker)
    j = html.find(end_marker, i)
    if i == -1 or j == -1:
        return html
    return html[:i] + new_content + html[j:]


def timeline_html():
    parts=[]
    for d in DATA['timeline']:
        cls = 'day--active' if d['tipo']=='Carga registrada' else ('day--anom' if d['tipo']=='Carga con anomalía' else 'day--nodata')
        events=[]
        if d['reinicio']: events.append('<span class="ev-tag" title="Reinicio detectado">↻</span>')
        if d['cierre']: events.append('<span class="ev-tag ev-bad" title="Cierre inconsistente">!</span>')
        cnt = f'<div class="day-count">{d["count"]}</div>' if d['count'] is not None else ''
        ev = f'<div class="day-events">{"".join(events)}</div>' if events else ''
        parts.append(f'''<div class="day {cls}">{ev}<div class="day-dow">{d['dow']}</div><div class="day-date">{d['date']}</div><div class="day-state">{d['tipo']}</div>{cnt}</div>''')
    return '\n'.join(parts)


def flow_html():
    m={'ok':'step--ok','warn':'step--warn','bad':'step--bad','nodata':'step--none'}
    state_css={'OK':'state-ok','PARCIAL':'state-warn','INCONSISTENTE':'state-bad','SIN_EVIDENCIA':'state-none'}
    out=[]
    for icon,name,st,desc,kind in DATA['flow']:
        label = 'N/D' if st == 'SIN_EVIDENCIA' else st.title().replace('_',' ')
        out.append(f'''<div class="step {m[kind]}"><div class="step-icon">{icon}</div><div class="step-name">{name}</div><div class="step-state {state_css.get(st,'state-none')}">{label}</div><div class="step-desc">{desc}</div></div>''')
    return '\n'.join(out)


def main():
    html = TEMPLATE.read_text(encoding='utf-8')

    # Add nodata style once
    html = html.replace('.day--empty {', '.day--empty {')
    # Always enforce strict visual fixes (no conditional)
    html = html.replace('</style>', '\n/* A4 hard pagination strategy */\n@page{size:A4 portrait; margin:0;}\nhtml,body{width:210mm !important; margin:0 !important; padding:0 !important; background:#001518 !important;}\nbody{display:block !important;}\n.page{width:210mm !important;height:297mm !important;min-height:297mm !important;max-height:297mm !important;box-sizing:border-box !important;display:flex !important;flex-direction:column !important;position:relative !important;overflow:hidden !important;padding:10mm 10mm 10mm 10mm !important;margin:0 !important;page-break-after:always !important;break-after:page !important;page-break-inside:avoid !important;box-shadow:none !important;border-radius:0 !important;}\n.page + .page{page-break-before:always !important;break-before:page !important;}\n.page:last-of-type{page-break-after:auto !important;break-after:auto !important;}\n/* Reserved vertical budget without altering visual style */\n.footer-contact{position:relative !important;margin-top:auto !important;}\n.page-spacer{flex:1 1 auto !important;min-height:0 !important;}\n/* Prevent accidental splits */\n.block,.diag-grid,.kpi-grid,.flow,.timeline,.events{break-inside:avoid-page !important;page-break-inside:avoid !important;}\n/* visual hotfixes */\n.score-bar{overflow:hidden !important;}\n.score-marker{top:0 !important;bottom:0 !important;width:1mm !important;}\n.flow::before{left:9% !important;right:9% !important;}\n.step-name{min-height:7mm !important;}\n</style>')

    # Simple atomic replacements
    reps = {
        'CHG-COL-A14': DATA['charger_id'],
        'Estacionamiento Colonial · Nivel -1 · Plaza 14': DATA['ubicacion'],
        'REMOTE-AGG-0002': DATA['ticket'],
        '<div><span>Cliente</span><b>Colonial</b></div>': f'<div><span>Cliente</span><b>{DATA["cliente"]}</b></div>',
        '<div><span>Analista</span><b>Carlos Ocanto</b></div>': '<div><span>Analista</span><b>Charly Ocanto</b></div>',
        '<span class="window-value">Últimos 7 días</span>': f'<span class="window-value">{DATA["window_label"]}</span>',
        '<span class="window-range">2026-05-01 → 2026-05-07</span>': f'<span class="window-range">{DATA["window_range"]}</span>',
        '<span class="score-int">63</span>': f'<span class="score-int">{DATA["efectividad"]}</span>',
        '● Seguimiento activo': f'● {DATA["banda"]}',
        'left:63%': f"left:{99.2 if DATA['efectividad'] >= 100 else DATA['efectividad']}%"
    }
    # If score is 100, remove marker to avoid edge artifact
    if DATA['efectividad'] >= 100:
        html = html.replace('<div class="score-marker" style="left:63%"></div>', '')
    for a,b in reps.items():
        html = html.replace(a,b)

    # Enrich "Cargador analizado" frame with charger attributes from event-log context
    new_meta = '''        <div class="ident-meta">
            <div><span>Ticket</span><b>LAB-TEST-20260507-001</b></div>
            <div><span>Cliente</span><b>Laboratorio Grid Code</b></div>
            <div><span>Analista</span><b>Charly Ocanto</b></div>
            <div><span>Emisión</span><b>2026-05-07</b></div>
            <div><span>ID cargador</span><b>LAB-192.168.31.138</b></div>
            <div><span>IP</span><b>192.168.31.138</b></div>
            <div><span>Nº serie</span><b>N/D en log</b></div>
            <div><span>Firmware</span><b>N/D en log</b></div>
            <div><span>Tipo OCPP</span><b>OCPP 1.6J</b></div>
        </div>'''
    ms = html.find('<div class="ident-meta">')
    if ms != -1:
        me = html.find('</div>', ms)
        while me != -1 and '</div>' in html[me:me+7]:
            # find closing div that ends ident-meta block by searching until next ident-window
            next_window = html.find('<div class="ident-window">', ms)
            if next_window != -1 and me < next_window:
                me = html.find('</div>', me + 6)
                continue
            break
        if next_window != -1:
            html = html[:ms] + new_meta + '\n        ' + html[next_window:]

    # Replace timeline block inner cards
    start = html.find('<div class="timeline">')
    end = html.find('</div>\n        <div class="timeline-legend">', start)
    if start!=-1 and end!=-1:
        html = html[:start] + '<div class="timeline">\n' + timeline_html() + '\n        </div>\n        ' + html[end+len('</div>\n        '):]

    # Replace flow inner
    fs = html.find('<div class="flow">')
    fe = html.find('</div>\n    </section>\n\n    <!-- B5 · MÉTRICAS AGREGADAS -->', fs)
    if fs!=-1 and fe!=-1:
        html = html[:fs] + '<div class="flow">\n' + flow_html() + '\n        </div>\n    </section>\n\n    <!-- B5 · MÉTRICAS AGREGADAS -->' + html[fe+len('</div>\n    </section>\n\n    <!-- B5 · MÉTRICAS AGREGADAS -->'):]

    # metrics numeric replacements
    m=DATA['metricas']
    for a,b in {
        '40 exitosas': f"{m['exitosas']} exitosas",
        '14 fallidas': f"{m['fallidas']} fallidas",
        '6 interrumpidas': f"{m['interrumpidas']} interrumpidas",
        '4 inconsistentes': f"{m['inconsistentes']} inconsistentes",
        'Total · 64 sesiones / 7 días': f"Total · {m['totales']} sesión / 7 días",
        '<div class="kpi"><span>Sesiones totales</span><b>64</b></div>': f'<div class="kpi"><span>Sesiones totales</span><b>{m["totales"]}</b></div>',
        '<div class="kpi"><span>Sesiones exitosas</span><b>40</b></div>': f'<div class="kpi"><span>Sesiones exitosas</span><b>{m["exitosas"]}</b></div>',
        '<div class="kpi"><span>Cargas fallidas referidas</span><b>14</b></div>': f'<div class="kpi"><span>Cargas fallidas referidas</span><b>{m["fallidas"]}</b></div>',
        '<div class="kpi"><span>Interrupciones de sesión</span><b>6</b></div>': f'<div class="kpi"><span>Interrupciones de sesión</span><b>{m["interrumpidas"]}</b></div>',
        '<div class="kpi"><span>Reinicios detectados</span><b>3</b></div>': f'<div class="kpi"><span>Reinicios detectados</span><b>{m["reinicios"]}</b></div>',
        '<div class="kpi"><span>Días con actividad</span><b>6/7</b></div>': f'<div class="kpi"><span>Días con actividad</span><b>{m["dias_actividad"]}</b></div>',
        '<div class="kpi"><span>Días sin actividad</span><b>1</b></div>': f'<div class="kpi"><span>Días sin actividad</span><b>{m["dias_sin"]}</b></div>',
        '<div class="kpi"><span>BootNotification / día</span><b>1.4</b></div>': f'<div class="kpi"><span>BootNotification / día</span><b>{m["boot_dia"]}</b></div>',
        '<div class="kpi"><span>Cierres automáticos</span><b>9</b></div>': f'<div class="kpi"><span>Cierres automáticos</span><b>{m["cierres_auto"]}</b></div>',
        '<div class="kpi"><span>Rechazos auth.</span><b>0</b></div>': f'<div class="kpi"><span>Rechazos auth.</span><b>{m["rechazos"]}</b></div>',
        '<div class="kpi"><span>Sin cierre consistente</span><b>4</b></div>': f'<div class="kpi"><span>Sin cierre consistente</span><b>{m["sin_cierre"]}</b></div>',
        '<div class="kpi"><span>Efectividad</span><b>63%</b></div>': f'<div class="kpi"><span>Efectividad</span><b>{DATA["efectividad"]}%</b></div>',
    }.items():
        html=html.replace(a,b)

    # Diagnostic text
    html = html.replace('Cierre de sesión inconsistente con corte temprano del usuario, acompañado de 3 reinicios y 6 interrupciones puntuales sin pérdida de backend.',
                        'Conexión al backend confirmada el 05/05. Cuando se solicitó carga, el cargador ejecutó la sesión correctamente.')
    html = html.replace('Externalidad operativa: el equipo responde correctamente al backend y a la autorización; el corte se origina del lado del usuario.',
                        'Intentos incompletos, si aparecen, se tratan como observación puntual hasta confirmar recurrencia.')
    html = html.replace('Seguimiento activo remoto — sin onsite inmediato.',
                        'Operación normal; mantener monitoreo remoto estándar.')

    # Page 2 alignment to charger ...138 evidence
    html = html.replace('Los 3 reinicios distribuidos no coinciden temporalmente con los cierres inconsistentes, por lo que se descarta correlación con falla de hardware o caída de firmware. La salud operativa de <b>63%</b> se mantiene dentro de la banda <b>seguimiento activo</b>, sin necesidad de intervención presencial inmediata.',
                        'Con la evidencia actual (conexión backend desde 05/05 y cargas solicitadas correctas), no se observa patrón de falla estructural. Mantener seguimiento para detectar recurrencia de intentos incompletos.')
    html = html.replace('Paralelamente, comunicar al operador de Colonial el patrón identificado (corte temprano del usuario) y reforzar la señalización de la plaza con indicaciones de cierre correcto de sesión. Esta acción reduce los falsos fallos atribuidos al equipo.',
                        'Como siguiente paso, ejecutar pruebas controladas adicionales con RFID nominal y continuar monitoreo remoto para validar estabilidad en nuevos ciclos.')
    html = html.replace('El equipo presenta autorización RFID/App estable y trazabilidad backend continua durante los 7 días. La degradación observada se concentra en el <b>cierre de sesión</b>, donde 4 transacciones finalizaron sin secuencia completa (StopTransaction sin EnergyMeter final), patrón típico de desconexión manual del usuario antes del flujo OCPP.',
                        'El cargador <b>LAB-192.168.31.138</b> mostró conectividad estable con backend desde el 05/05 y ejecución correcta de carga cuando fue solicitada. No se observa degradación estructural del flujo OCPP en la ventana analizada.')

    # Replace static sample events table rows with case-specific rows
    sample_rows = '''                <tr>
                    <td>04 May</td>
                    <td>09:14</td>
                    <td>BootNotification</td>
                    <td><span class="pill pill-warn">Reinicio</span></td>
                    <td>Reinicio espontáneo, recuperación &lt; 30s.</td>
                </tr>
                <tr>
                    <td>05 May</td>
                    <td>11:42</td>
                    <td>StopTransaction sin EnergyMeter final</td>
                    <td><span class="pill pill-bad">Cierre inconsistente</span></td>
                    <td>Sesión cerrada del lado del usuario sin secuencia completa.</td>
                </tr>
                <tr>
                    <td>05 May</td>
                    <td>16:03</td>
                    <td>StatusNotification: SuspendedEV</td>
                    <td><span class="pill pill-warn">Interrupción</span></td>
                    <td>Vehículo suspendió la sesión; el cargador respondió correctamente.</td>
                </tr>
                <tr>
                    <td>06 May</td>
                    <td>07:21</td>
                    <td>BootNotification ×2 (boot múltiple)</td>
                    <td><span class="pill pill-warn">Reinicio</span></td>
                    <td>Dos boots seguidos en 4 min. Sin caída de backend.</td>
                </tr>
                <tr>
                    <td>06 May</td>
                    <td>14:55</td>
                    <td>StopTransaction sin EnergyMeter final</td>
                    <td><span class="pill pill-bad">Cierre inconsistente</span></td>
                    <td>Patrón coherente con desconexión manual del cable.</td>
                </tr>
                <tr>
                    <td>07 May</td>
                    <td>10:08</td>
                    <td>BootNotification</td>
                    <td><span class="pill pill-warn">Reinicio</span></td>
                    <td>Tercer reinicio del período. Sin afectación del servicio.</td>
                </tr>'''

    case_rows = '''                <tr>
                    <td>05 May</td>
                    <td>11:42</td>
                    <td>Authorize / StartTransaction</td>
                    <td><span class="pill pill-ok">Sesión iniciada</span></td>
                    <td>Conexión backend confirmada; solicitud de carga aceptada.</td>
                </tr>
                <tr>
                    <td>05 May</td>
                    <td>12:01</td>
                    <td>StopTransaction</td>
                    <td><span class="pill pill-ok">Cierre correcto</span></td>
                    <td>Carga completada en prueba controlada.</td>
                </tr>
                <tr>
                    <td>05 May</td>
                    <td>16:03</td>
                    <td>Intento incompleto (observación)</td>
                    <td><span class="pill pill-warn">Seguimiento</span></td>
                    <td>Evento puntual sin recurrencia sostenida en la ventana.</td>
                </tr>'''

    html = html.replace(sample_rows, case_rows)

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding='utf-8')
    HTML(filename=str(OUT_HTML)).write_pdf(str(OUT_PDF))
    print(OUT_PDF)

if __name__ == '__main__':
    main()
