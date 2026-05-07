#!/usr/bin/env python3
from __future__ import annotations

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter

BASE = "/home/laia/.hermes/cache/documents/reporte_remoto_base_oficial.pdf"
OUT = "/home/laia/gridcode-protocol-hub/out/reporte_agregado_192_168_31_138.pdf"
OVL = "/home/laia/gridcode-protocol-hub/out/reporte_agregado_overlay_192_168_31_138.pdf"

# Coordenadas ajustadas sobre la base aprobada (A4)
FIELDS = [
    (58, 742, "Ticket: LAB-TEST-20260507-001"),
    (58, 726, "Cliente/Sitio: Laboratorio"),
    (58, 710, "Cargador: LAB-192.168.31.138  |  IP: 192.168.31.138"),
    (58, 694, "Conectividad remota: SI"),
    (58, 678, "Fecha analisis: 2026-05-07 12:20 CEST  |  Analista: Laia"),

    (58, 646, "Estado backend/enlace: Operativo"),
    (58, 630, "Placa comunicaciones: Operativa"),
    (58, 614, "Observacion conectividad: Acceso Web UI y descarga OCPP OK"),

    (58, 582, "Endpoint OCPP antes: ws://192.168.31.165/ws/ocpp"),
    (58, 566, "Endpoint objetivo: ws://192.168.31.165/ws/ocpp"),
    (58, 550, "Endpoint despues: ws://192.168.31.165/ws/ocpp (persistido: SI)"),

    (58, 518, "Ultima carga: 2026-05-05 14:56:49 CEST"),
    (58, 502, "Duracion ultima carga: 00:19:40"),
    (58, 486, "idTag detectado: #freecharging  |  Modo Free: SI"),
    (58, 470, "Resultado de carga: sesion registrada; idTagInfo backend = Invalid"),

    (58, 438, "Sesiones 7d: 1  |  Exitosas: 0  |  Failed starts: 0  |  Interrupciones: 0"),
    (58, 422, "Clasificacion criticidad: seguimiento"),

    (58, 390, "Evidencia log: OCPP_logs_20260507_110108.zip (5004219 bytes)"),
    (58, 374, "Acciones remotas: validacion endpoint + descarga y analisis OCPP"),
    (58, 358, "Decision: mantener monitoreo remoto, onsite no requerido por ahora"),
]


def make_overlay(path: str):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 9)
    for x, y, text in FIELDS:
        c.drawString(x, y, text)
    c.save()


def merge(base_pdf: str, overlay_pdf: str, out_pdf: str):
    base = PdfReader(base_pdf)
    ov = PdfReader(overlay_pdf)
    w = PdfWriter()
    page = base.pages[0]
    page.merge_page(ov.pages[0])
    w.add_page(page)
    with open(out_pdf, "wb") as f:
        w.write(f)


if __name__ == "__main__":
    make_overlay(OVL)
    merge(BASE, OVL, OUT)
    print(OUT)
