from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Criticity = Literal["sano", "seguimiento", "alta", "maxima"]


@dataclass
class RemoteDashboardReport:
    ticket_id: str
    charger_id: str
    charger_ip: str
    site_name: str
    endpoint_before: str
    endpoint_target: str
    endpoint_after: str
    endpoint_saved: bool
    last_charge_at_cest: str
    last_charge_duration: str
    idtag_used: str
    free_mode_detected: bool
    charge_result: str
    sessions_total_7d: int
    sessions_ok_7d: int
    failed_starts_7d: int
    interruptions_7d: int
    criticity: Criticity
    analyst_name: str
    report_date_cest: str

    def validate(self) -> tuple[bool, str]:
        if not self.ticket_id.strip():
            return False, "missing_ticket_id"
        if not self.charger_id.strip():
            return False, "missing_charger_id"
        if self.sessions_total_7d < 0:
            return False, "invalid_sessions_total_7d"
        if self.sessions_ok_7d < 0:
            return False, "invalid_sessions_ok_7d"
        if self.criticity not in {"sano", "seguimiento", "alta", "maxima"}:
            return False, "invalid_criticity"
        return True, "ok"
