from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class OnsiteReportPayload:
    ticket_id: str
    charger_id: str
    technician_name: str
    receiver_name: str
    checklist_choices_completed: bool
    observations: str
    photos_paths: List[str] = field(default_factory=list)
    onsite_report_path: str = ""

    def validate(self) -> tuple[bool, str]:
        if not self.ticket_id.strip():
            return False, "missing_ticket_id"
        if not self.charger_id.strip():
            return False, "missing_charger_id"
        if not self.technician_name.strip():
            return False, "missing_technician_name"
        if not self.receiver_name.strip():
            return False, "missing_receiver_name"
        return True, "ok"
