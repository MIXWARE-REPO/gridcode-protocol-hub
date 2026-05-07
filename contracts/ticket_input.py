from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class TicketInput:
    ticket_id: str
    customer_name: str
    site_name: str
    charger_id: str
    charger_ip: str
    requester_email: str
    participants: List[str] = field(default_factory=list)

    def validate(self) -> tuple[bool, str]:
        if not self.ticket_id.strip():
            return False, "missing_ticket_id"
        if not self.charger_id.strip():
            return False, "missing_charger_id"
        if not self.requester_email.strip():
            return False, "missing_requester_email"
        return True, "ok"
