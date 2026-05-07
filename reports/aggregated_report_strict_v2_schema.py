from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AggregatedReportV2:
    # Header
    report_title: str
    report_subtitle: str
    report_date_cest: str

    # Frame A - Identificación
    ticket_id: str
    customer_site: str
    charger_label: str
    charger_ip: str
    analyst_name: str

    # Frame B - Conectividad
    backend_status: str
    comms_board_status: str
    connectivity_notes: str

    # Frame C - OCPP endpoint
    endpoint_before: str
    endpoint_target: str
    endpoint_after: str
    endpoint_persisted: str

    # Frame D - Actividad
    last_charge_at_cest: str
    last_charge_duration: str
    idtag_used: str
    free_mode: str
    charge_result: str

    # Frame E - Métricas 7d
    sessions_total_7d: str
    sessions_ok_7d: str
    failed_starts_7d: str
    interruptions_7d: str
    criticity_band: str

    # Frame F - Decisión
    evidence_ref: str
    remote_actions: str
    final_decision: str

    # Footer
    generated_by: str
    report_version: str

    def validate(self) -> tuple[bool, str]:
        required = [
            self.ticket_id,
            self.charger_label,
            self.charger_ip,
            self.endpoint_after,
            self.last_charge_at_cest,
            self.final_decision,
        ]
        if any(not str(x).strip() for x in required):
            return False, "missing_required_fields"
        return True, "ok"
