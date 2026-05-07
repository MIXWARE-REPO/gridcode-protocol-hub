from __future__ import annotations

from typing import Dict, Any


def decide_next_step(remote_result: Dict[str, Any]) -> Dict[str, Any]:
    """Puente de decisión entre Grupo 2 y Grupo 3."""
    if not remote_result.get("executed", False):
        return {"next": "group3_onsite", "reason": "remote_not_executed"}

    if remote_result.get("requires_onsite", False):
        return {"next": "group3_onsite", "reason": remote_result.get("reason", "escalated")}

    return {"next": "close_remote", "reason": "resolved_remote"}
