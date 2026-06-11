#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader, PdfWriter
from weasyprint import HTML

TEMPLATE = Path('/home/laia/gridcode-protocol-hub/templates/forms/form-remotes/v1/template.html')
OUT_DIR = Path('/home/laia/gridcode-protocol-hub/out')
OUT_FINAL = OUT_DIR / 'form-remotes-192.168.31.138-a4-split.pdf'


def apply_replacements(html: str) -> str:
    reps = {
        'CHG-COL-A14': 'LAB-192.168.31.138',
        'Estacionamiento Colonial · Nivel -1 · Plaza 14': 'Laboratorio Grid Code · Red local · Banco de pruebas',
        'REMOTE-AGG-0002': 'LAB-TEST-20260507-001',
        '<div><span>Cliente</span><b>Colonial</b></div>': '<div><span>Cliente</span><b>Laboratorio Grid Code</b></div>',
        '<div><span>Analista</span><b>Carlos Ocanto</b></div>': '<div><span>Analista</span><b>Laia</b></div>',
        '<span class="score-int">63</span>': '<span class="score-int">100</span>',
        '● Seguimiento activo': '● Sano',
        'left:63%': 'left:99.2%',

        '40 exitosas': '1 exitosa',
        '14 fallidas': '0 fallidas',
        '6 interrumpidas': '0 interrumpidas',
        '4 inconsistentes': '0 inconsistentes',
        'Total · 64 sesiones / 7 días': 'Total · 1 sesión / 7 días',
        '<div class="kpi"><span>Sesiones totales</span><b>64</b></div>': '<div class="kpi"><span>Sesiones totales</span><b>1</b></div>',
        '<div class="kpi"><span>Sesiones exitosas</span><b>40</b></div>': '<div class="kpi"><span>Sesiones exitosas</span><b>1</b></div>',
        '<div class="kpi"><span>Cargas fallidas referidas</span><b>14</b></div>': '<div class="kpi"><span>Cargas fallidas referidas</span><b>0</b></div>',
        '<div class="kpi"><span>Interrupciones de sesión</span><b>6</b></div>': '<div class="kpi"><span>Interrupciones de sesión</span><b>0</b></div>',
        '<div class="kpi"><span>Reinicios detectados</span><b>3</b></div>': '<div class="kpi"><span>Reinicios detectados</span><b>0</b></div>',
        '<div class="kpi"><span>Días con actividad</span><b>6/7</b></div>': '<div class="kpi"><span>Días con actividad</span><b>1/7</b></div>',
        '<div class="kpi"><span>Días sin actividad</span><b>1</b></div>': '<div class="kpi"><span>Días sin actividad</span><b>6</b></div>',
        '<div class="kpi"><span>BootNotification / día</span><b>1.4</b></div>': '<div class="kpi"><span>BootNotification / día</span><b>0.0</b></div>',
        '<div class="kpi"><span>Cierres automáticos</span><b>9</b></div>': '<div class="kpi"><span>Cierres automáticos</span><b>1</b></div>',
        '<div class="kpi"><span>Sin cierre consistente</span><b>4</b></div>': '<div class="kpi"><span>Sin cierre consistente</span><b>0</b></div>',
        '<div class="kpi"><span>Efectividad</span><b>63%</b></div>': '<div class="kpi"><span>Efectividad</span><b>100%</b></div>',

        'Cierre de sesión inconsistente con corte temprano del usuario, acompañado de 3 reinicios y 6 interrupciones puntuales sin pérdida de backend.': 'Conexión al backend confirmada el 05/05. Cuando se solicitó carga, el cargador ejecutó la sesión correctamente.',
        'Externalidad operativa: el equipo responde correctamente al backend y a la autorización; el corte se origina del lado del usuario.': 'Intentos incompletos, si aparecen, se tratan como observación puntual hasta confirmar recurrencia.',
        'Seguimiento activo remoto — sin onsite inmediato.': 'Operación normal; mantener monitoreo remoto estándar.',
    }
    for a, b in reps.items():
        html = html.replace(a, b)

    # hide score marker at 100 to avoid artifact
    html = html.replace('<div class="score-marker" style="left:63%"></div>', '')

    # timeline: only 05 May active
    html = html.replace('<div class="day day--active">\n                <div class="day-dow">Vie</div>\n                <div class="day-date">01 May</div>\n                <div class="day-state">Carga registrada</div>\n                <div class="day-count">5</div>\n            </div>', '<div class="day day--empty"><div class="day-dow">Vie</div><div class="day-date">01 May</div><div class="day-state">Sin carga registrada</div></div>')
    html = html.replace('<div class="day day--active">\n                <div class="day-dow">Sáb</div>\n                <div class="day-date">02 May</div>\n                <div class="day-state">Carga registrada</div>\n                <div class="day-count">8</div>\n            </div>', '<div class="day day--empty"><div class="day-dow">Sáb</div><div class="day-date">02 May</div><div class="day-state">Sin carga registrada</div></div>')
    html = html.replace('<div class="day day--active">\n                <div class="day-dow">Lun</div>\n                <div class="day-date">04 May</div>\n                <div class="day-state">Carga registrada</div>\n                <div class="day-count">12</div>\n            </div>', '<div class="day day--empty"><div class="day-dow">Lun</div><div class="day-date">04 May</div><div class="day-state">Sin carga registrada</div></div>')
    html = html.replace('<div class="day day--anom">\n                <div class="day-events">\n                    <span class="ev-tag ev-bad" title="Cierre inconsistente">!</span>\n                </div>\n                <div class="day-dow">Mar</div>\n                <div class="day-date">05 May</div>\n                <div class="day-state">Carga con anomalía</div>\n                <div class="day-count">14</div>\n            </div>', '<div class="day day--active"><div class="day-dow">Mar</div><div class="day-date">05 May</div><div class="day-state">Carga registrada</div><div class="day-count">1</div></div>')
    html = html.replace('<div class="day day--anom">\n                <div class="day-events">\n                    <span class="ev-tag" title="Reinicio detectado">↻</span>\n                    <span class="ev-tag ev-bad" title="Cierre inconsistente">!</span>\n                </div>\n                <div class="day-dow">Mié</div>\n                <div class="day-date">06 May</div>\n                <div class="day-state">Carga con anomalía</div>\n                <div class="day-count">18</div>\n            </div>', '<div class="day day--empty"><div class="day-dow">Mié</div><div class="day-date">06 May</div><div class="day-state">Sin carga registrada</div></div>')
    html = html.replace('<div class="day day--active">\n                <div class="day-events">\n                    <span class="ev-tag" title="Reinicio detectado">↻</span>\n                </div>\n                <div class="day-dow">Jue</div>\n                <div class="day-date">07 May</div>\n                <div class="day-state">Carga registrada</div>\n                <div class="day-count">7</div>\n            </div>', '<div class="day day--empty"><div class="day-dow">Jue</div><div class="day-date">07 May</div><div class="day-state">Sin carga registrada</div></div>')

    return html


def split_articles(full_html: str):
    # robust selectors against class variations (page-break, continued, etc.)
    start1 = full_html.find('<article class="page page-break">')
    if start1 == -1:
        start1 = full_html.find('<article class="page">')
    end1 = full_html.find('</article>', start1) + len('</article>')

    start2 = full_html.find('<article class="page page--continued">', end1)
    end2 = full_html.find('</article>', start2) + len('</article>')

    head = full_html[: full_html.find('<body>') + len('<body>')]
    tail = '</body></html>'

    page1 = head + '\n' + full_html[start1:end1] + '\n' + tail
    page2 = head + '\n' + full_html[start2:end2] + '\n' + tail
    return page1, page2


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = apply_replacements(TEMPLATE.read_text(encoding='utf-8'))
    page1_html, page2_html = split_articles(html)

    p1_html = OUT_DIR / 'form-remotes-p1.html'
    p2_html = OUT_DIR / 'form-remotes-p2.html'
    p1_pdf = OUT_DIR / 'form-remotes-p1.pdf'
    p2_pdf = OUT_DIR / 'form-remotes-p2.pdf'

    p1_html.write_text(page1_html, encoding='utf-8')
    p2_html.write_text(page2_html, encoding='utf-8')

    HTML(filename=str(p1_html)).write_pdf(str(p1_pdf))
    HTML(filename=str(p2_html)).write_pdf(str(p2_pdf))

    writer = PdfWriter()
    for p in PdfReader(str(p1_pdf)).pages:
        writer.add_page(p)
    for p in PdfReader(str(p2_pdf)).pages:
        writer.add_page(p)
    with OUT_FINAL.open('wb') as f:
        writer.write(f)

    print(OUT_FINAL)


if __name__ == '__main__':
    main()
