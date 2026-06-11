
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WebastoUniteLogReport:
    title: str
    charger_id: str
    charger_ip: str
    building: str
    ticket_id: str
    log_zip_name: str
    log_zip_bytes: int
    generated_at_cest: str
    analyst_name: str = "Laia"
    summary: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    daily_rows: list[dict[str, Any]] = field(default_factory=list)
    notable_events: list[dict[str, Any]] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    evidence_files: list[dict[str, Any]] = field(default_factory=list)

    def validate(self) -> tuple[bool, str]:
        if not self.title.strip():
            return False, "missing_title"
        if not self.charger_id.strip():
            return False, "missing_charger_id"
        if not self.charger_ip.strip():
            return False, "missing_charger_ip"
        if not self.log_zip_name.strip():
            return False, "missing_log_zip_name"
        if self.log_zip_bytes < 0:
            return False, "invalid_log_zip_bytes"
        return True, "ok"
