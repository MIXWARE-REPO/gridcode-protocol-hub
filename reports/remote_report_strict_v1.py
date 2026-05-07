from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


@dataclass
class RemoteReportInput:
    ticket_id: str
    charger_id: str
    charger_ip: str
    site_name: str
    endpoint_before: str
    endpoint_target: str
    endpoint_after: str
    endpoint_saved: bool
    last_charge_at_cet: str
    last_charge_duration: str
    idtag_used: str
    free_mode_detected: bool
    charge_result: str
    log_zip_name: str
    log_zip_bytes: int
    analyst_name: str = "Laia"


def build_strict_payload(data: RemoteReportInput) -> Dict[str, Any]:
    """Payload canónico para poblar plantilla validada (sin variar estructura)."""
    return {
        "meta.report_version": "remote_strict_v1",
        "meta.generated_at": datetime.utcnow().isoformat() + "Z",
        "ticket.id": data.ticket_id,
        "charger.id": data.charger_id,
        "charger.ip": data.charger_ip,
        "site.name": data.site_name,
        "ocpp.endpoint.before": data.endpoint_before,
        "ocpp.endpoint.target": data.endpoint_target,
        "ocpp.endpoint.after": data.endpoint_after,
        "ocpp.endpoint.saved": "SI" if data.endpoint_saved else "NO",
        "activity.last_charge_at_cet": data.last_charge_at_cet,
        "activity.last_charge_duration": data.last_charge_duration,
        "activity.idtag": data.idtag_used,
        "activity.free_mode": "SI" if data.free_mode_detected else "NO",
        "activity.charge_result": data.charge_result,
        "evidence.log_zip_name": data.log_zip_name,
        "evidence.log_zip_bytes": str(data.log_zip_bytes),
        "analyst.name": data.analyst_name,
        "summary": (
            f"Endpoint before: {data.endpoint_before} | after: {data.endpoint_after}. "
            f"Última carga: {data.last_charge_at_cet} ({data.last_charge_duration}). "
            f"idTag: {data.idtag_used}."
        ),
    }


def render_pdf_from_template(template_pdf: str, output_pdf: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Relleno estricto de plantilla PDF (AcroForm).
    Requiere pypdf instalado. Solo completa campos existentes: no rediseña ni overlay.
    """
    from pypdf import PdfReader, PdfWriter

    template_path = Path(template_pdf)
    if not template_path.exists():
        raise FileNotFoundError(f"Template no encontrado: {template_pdf}")

    reader = PdfReader(str(template_path))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # AcroForm preservation
    if "/AcroForm" in reader.trailer["/Root"]:
        writer._root_object.update({"/AcroForm": reader.trailer["/Root"]["/AcroForm"]})

    for i in range(len(writer.pages)):
        writer.update_page_form_field_values(writer.pages[i], payload)

    out = Path(output_pdf)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as f:
        writer.write(f)

    return {
        "template_pdf": str(template_path),
        "output_pdf": str(out),
        "fields_written": len(payload),
    }
