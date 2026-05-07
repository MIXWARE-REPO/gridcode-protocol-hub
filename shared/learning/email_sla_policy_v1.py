from __future__ import annotations

from typing import Dict, Any

SLA_POLICY = {
    "p1": {
        "sin_respuesta_alert_hours": 24,
        "pidio_ajuste_same_day": True,
    },
    "p2": {
        "sin_respuesta_alert_hours": 48,
        "pidio_ajuste_same_day": True,
    },
}


def get_sla(priority: str) -> Dict[str, Any]:
    p = (priority or "p2").lower()
    return SLA_POLICY.get(p, SLA_POLICY["p2"])
