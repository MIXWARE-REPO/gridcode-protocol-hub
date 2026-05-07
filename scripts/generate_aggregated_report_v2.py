#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from reports.aggregated_report_strict_v2_schema import AggregatedReportV2
from reports.aggregated_report_strict_v2_renderer import render_html, render_pdf

DATA = {
    "report_title": "Informe de Análisis Agregado",
    "report_subtitle": "SLA Colonial · Diagnóstico remoto OCPP · Formato estricto",
    "report_date_cest": "2026-05-07 12:35 CEST",
    "ticket_id": "LAB-TEST-20260507-001",
    "customer_site": "Laboratorio",
    "charger_label": "LAB-192.168.31.138",
    "charger_ip": "192.168.31.138",
    "analyst_name": "Laia",
    "backend_status": "Operativo",
    "comms_board_status": "Operativa",
    "connectivity_notes": "Login Web UI y descarga OCPP completados",
    "endpoint_before": "ws://192.168.31.165/ws/ocpp",
    "endpoint_target": "ws://192.168.31.165/ws/ocpp",
    "endpoint_after": "ws://192.168.31.165/ws/ocpp",
    "endpoint_persisted": "SI",
    "last_charge_at_cest": "2026-05-05 14:56:49 CEST",
    "last_charge_duration": "00:19:40",
    "idtag_used": "#freecharging",
    "free_mode": "SI",
    "charge_result": "Sesión registrada; backend respondió idTagInfo=Invalid",
    "sessions_total_7d": "1",
    "sessions_ok_7d": "0",
    "failed_starts_7d": "0",
    "interruptions_7d": "0",
    "criticity_band": "seguimiento",
    "evidence_ref": "OCPP_logs_20260507_110108.zip (5004219 bytes)",
    "remote_actions": "Validación endpoint + descarga/análisis de logs",
    "final_decision": "Monitoreo remoto activo; onsite no requerido por ahora",
    "generated_by": "Grid Code / Laia",
    "report_version": "aggregated_strict_v2",
}

if __name__ == "__main__":
    report = AggregatedReportV2(**DATA)
    out_html = "/home/laia/gridcode-protocol-hub/out/aggregated_report_192_168_31_138_v2.html"
    out_pdf = "/home/laia/gridcode-protocol-hub/out/aggregated_report_192_168_31_138_v2.pdf"
    html = render_html(report, out_html)
    pdf = render_pdf(html, out_pdf)
    print(json.dumps({"html": html, "pdf": pdf}, ensure_ascii=False))
