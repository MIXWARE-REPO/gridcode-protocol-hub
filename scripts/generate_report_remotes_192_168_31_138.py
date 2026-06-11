#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from weasyprint import HTML

TEMPLATE = Path("/home/laia/gridcode-protocol-hub/templates/forms/form-remotes/v1/template.html")
OUT_HTML = Path("/home/laia/gridcode-protocol-hub/out/form-remotes-192.168.31.138.html")
OUT_PDF = Path("/home/laia/gridcode-protocol-hub/out/form-remotes-192.168.31.138.pdf")


def main() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")

    replacements = {
        "CHG-COL-A14": "LAB-192.168.31.138",
        "Estacionamiento Colonial · Nivel -1 · Plaza 14": "Laboratorio Grid Code · Red local · Banco de pruebas",
        "REMOTE-AGG-0002": "LAB-TEST-20260507-001",
        "<div><span>Cliente</span><b>Colonial</b></div>": "<div><span>Cliente</span><b>Laboratorio Grid Code</b></div>",
        "<div><span>Analista</span><b>Carlos Ocanto</b></div>": "<div><span>Analista</span><b>Laia</b></div>",
        "<div><span>Emisión</span><b>2026-05-07</b></div>": "<div><span>Emisión</span><b>2026-05-07</b></div>",
        "2026-05-01 → 2026-05-07": "2026-05-01 → 2026-05-07",
        "<span class=\"score-int\">63</span>": "<span class=\"score-int\">100</span>",
        "● Seguimiento activo": "● Sano",
        "left:63%": "left:100%",
        "40 exitosas": "1 exitosa",
        "14 fallidas": "0 fallidas",
        "6 interrumpidas": "0 interrumpidas",
        "4 inconsistentes": "0 inconsistentes",
        "Total · 64 sesiones / 7 días": "Total · 1 sesión / 7 días",
        "<div class=\"kpi\"><span>Sesiones totales</span><b>64</b></div>": "<div class=\"kpi\"><span>Sesiones totales</span><b>1</b></div>",
        "<div class=\"kpi\"><span>Sesiones exitosas</span><b>40</b></div>": "<div class=\"kpi\"><span>Sesiones exitosas</span><b>1</b></div>",
        "<div class=\"kpi\"><span>Cargas fallidas referidas</span><b>14</b></div>": "<div class=\"kpi\"><span>Cargas fallidas referidas</span><b>0</b></div>",
        "<div class=\"kpi\"><span>Interrupciones de sesión</span><b>6</b></div>": "<div class=\"kpi\"><span>Interrupciones de sesión</span><b>0</b></div>",
        "<div class=\"kpi\"><span>Reinicios detectados</span><b>3</b></div>": "<div class=\"kpi\"><span>Reinicios detectados</span><b>0</b></div>",
        "<div class=\"kpi\"><span>Días con actividad</span><b>6/7</b></div>": "<div class=\"kpi\"><span>Días con actividad</span><b>1/7</b></div>",
        "<div class=\"kpi\"><span>Días sin actividad</span><b>1</b></div>": "<div class=\"kpi\"><span>Días sin actividad</span><b>6</b></div>",
        "<div class=\"kpi\"><span>BootNotification / día</span><b>1.4</b></div>": "<div class=\"kpi\"><span>BootNotification / día</span><b>0.0</b></div>",
        "<div class=\"kpi\"><span>Cierres automáticos</span><b>9</b></div>": "<div class=\"kpi\"><span>Cierres automáticos</span><b>1</b></div>",
        "<div class=\"kpi\"><span>Sin cierre consistente</span><b>4</b></div>": "<div class=\"kpi\"><span>Sin cierre consistente</span><b>0</b></div>",
        "<div class=\"kpi\"><span>Efectividad</span><b>63%</b></div>": "<div class=\"kpi\"><span>Efectividad</span><b>100%</b></div>",
        "Cierre de sesión inconsistente con corte temprano del usuario, acompañado de 3 reinicios y 6 interrupciones puntuales sin pérdida de backend.": "Conexión al backend confirmada el 05/05 y sesiones de carga ejecutadas correctamente cuando fueron solicitadas.",
        "Mala secuencia de uso": "Operación estable verificada",
        "Externalidad operativa: el equipo responde correctamente al backend y a la autorización; el corte se origina del lado del usuario.": "El cargador mantuvo conectividad backend y respondió correctamente ante solicitudes de carga.",
        "Seguimiento activo remoto — sin onsite inmediato.": "Operación normal; mantener monitoreo remoto estándar.",
        "Degradación sostenida <50% en los próximos 3 ciclos de análisis o aparición de desconexiones backend recurrentes.": "Escalar solo si aparecen fallas repetidas de carga o desconexión backend en próximos ciclos.",
        "Ajuste de parámetros de timeout y validación de cierre.": "Validación de endpoint OCPP y descarga de logs OCPP ejecutadas.",
        "Revisión de firmware y estado de conectividad.": "Verificación de conectividad Web UI y endpoint actual completada.",
        "Verificación de backend / autorizaciones y consistencia de eventos.": "Correlación de evento Start/Stop y revisión de idTag #freecharging completada.",
        "Recomendación al cliente: secuencia correcta de inicio / cierre para evitar falsos fallos.": "Siguiente prueba recomendada: RFID nominal (no free mode) para confirmar flujo de autorización.",
        "El equipo presenta autorización RFID/App estable y trazabilidad backend continua durante los 7 días. La degradación observada se concentra en el <b>cierre de sesión</b>, donde 4 transacciones finalizaron sin secuencia completa (StopTransaction sin EnergyMeter final), patrón típico de desconexión manual del usuario antes del flujo OCPP.": "Conexión al backend confirmada el 05/05. En las solicitudes de carga verificadas, el cargador ejecutó la carga correctamente; no se observa degradación sostenida del flujo principal.",
        "Los 3 reinicios distribuidos no coinciden temporalmente con los cierres inconsistentes, por lo que se descarta correlación con falla de hardware o caída de firmware. La salud operativa de <b>63%</b> se mantiene dentro de la banda <b>seguimiento activo</b>, sin necesidad de intervención presencial inmediata.": "Los intentos de ejecución incompletos, cuando aparecen, se registran como observación puntual de seguimiento y no como falla estructural mientras no haya recurrencia.",
        "https://logs.grid-code.tech/sessions/LAB-192.168.31.138?from=2026-05-01&to=2026-05-07": "https://logs.grid-code.tech/sessions/LAB-192.168.31.138?from=2026-05-01&to=2026-05-07",
    }

    for old, new in replacements.items():
        html = html.replace(old, new)

    # timeline simplification to real 7-day pattern known
    html = html.replace("<div class=\"day day--active\">\n                <div class=\"day-dow\">Vie</div>\n                <div class=\"day-date\">01 May</div>\n                <div class=\"day-state\">Carga registrada</div>\n                <div class=\"day-count\">5</div>\n            </div>",
                        "<div class=\"day day--empty\">\n                <div class=\"day-dow\">Vie</div>\n                <div class=\"day-date\">01 May</div>\n                <div class=\"day-state\">Sin carga registrada</div>\n            </div>")

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    HTML(filename=str(OUT_HTML)).write_pdf(str(OUT_PDF))
    print(str(OUT_PDF))


if __name__ == "__main__":
    main()
