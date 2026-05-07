from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RemoteRailResult:
    ticket_id: str
    charger_id: str
    executed: bool
    resolved_remote: bool
    requires_onsite: bool
    criticity_band: str
    report_path: str
    evidence_ref: str
    reason: str = ""


def run_group2_remote_rail(payload: Dict[str, Any]) -> RemoteRailResult:
    """
    Rail Grupo 2 (placeholder estricto):
    1) validar entrada ticket/cargador
    2) descargar/analizar OCPP 7d
    3) aplicar acciones remotas permitidas
    4) clasificar criticidad
    5) emitir reporte remoto plantilla fija
    6) decidir escalado onsite
    """
    ticket_id = str(payload.get("ticket_id", "")).strip()
    charger_id = str(payload.get("charger_id", "")).strip()

    if not ticket_id or not charger_id:
        return RemoteRailResult(
            ticket_id=ticket_id,
            charger_id=charger_id,
            executed=False,
            resolved_remote=False,
            requires_onsite=True,
            criticity_band="maxima",
            report_path="",
            evidence_ref="",
            reason="missing_ticket_or_charger",
        )

    # TODO: conectar adapters reales (vpn/ui/log/pdf)
    return RemoteRailResult(
        ticket_id=ticket_id,
        charger_id=charger_id,
        executed=True,
        resolved_remote=False,
        requires_onsite=True,
        criticity_band="alta",
        report_path="",
        evidence_ref="",
        reason="remote_execution_placeholder",
    )
