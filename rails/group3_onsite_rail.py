from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class OnsiteRailResult:
    ticket_id: str
    charger_id: str
    executed: bool
    onsite_report_path: str
    photos_received: bool
    receiver_name: str
    reason: str = ""


def run_group3_onsite_rail(payload: Dict[str, Any]) -> OnsiteRailResult:
    """
    Rail Grupo 3 (placeholder estricto):
    1) precompletar PDF onsite con ticket+cargador
    2) técnico completa choices+observaciones+receptor
    3) consolidar evidencias fotográficas
    4) emitir reporte de visita
    """
    ticket_id = str(payload.get("ticket_id", "")).strip()
    charger_id = str(payload.get("charger_id", "")).strip()

    if not ticket_id or not charger_id:
        return OnsiteRailResult(
            ticket_id=ticket_id,
            charger_id=charger_id,
            executed=False,
            onsite_report_path="",
            photos_received=False,
            receiver_name="",
            reason="missing_ticket_or_charger",
        )

    return OnsiteRailResult(
        ticket_id=ticket_id,
        charger_id=charger_id,
        executed=True,
        onsite_report_path="",
        photos_received=False,
        receiver_name="",
        reason="onsite_execution_placeholder",
    )
