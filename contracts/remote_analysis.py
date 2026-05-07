from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RemoteAnalysisResult:
    ticket_id: str
    charger_id: str
    period_days: int
    sessions_total: int
    sessions_success: int
    interruptions: int
    failed_starts: int
    session_close_failures: int
    reboot_detected: bool
    activity_pct: float
    criticity_band: str  # sano|seguimiento|alta|maxima
    resolved_remote: bool
    requires_onsite: bool
    remote_report_path: str
    evidence_ref: str

    def validate(self) -> tuple[bool, str]:
        if self.period_days <= 0:
            return False, "invalid_period"
        if self.criticity_band not in {"sano", "seguimiento", "alta", "maxima"}:
            return False, "invalid_criticity_band"
        return True, "ok"
