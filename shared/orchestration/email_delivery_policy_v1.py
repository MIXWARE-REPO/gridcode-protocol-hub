from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

WORK_DAYS = {0, 1, 2, 3, 4}  # lun-vie
WORK_START_HOUR = 9
WORK_END_HOUR = 18

DEFAULT_CC = ["dario@grid-code.tech"]
ADMIN_EXTRA_CC = ["lorena@grid-code.tech"]
SUPPORT_EXTRA_CC = ["support@grid-code.tech"]


@dataclass
class DeliveryDecision:
    send_now: bool
    scheduled_for: str | None
    reason: str
    is_out_of_hours: bool = False
    suggestion_message: str = ""
    user_options: List[str] | None = None


def _next_business_morning(dt: datetime) -> datetime:
    probe = dt
    while True:
        if probe.weekday() in WORK_DAYS:
            morning = probe.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
            if probe <= morning:
                return morning
        probe = (probe + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


def _build_ooh_suggestion(now: datetime, scheduled: datetime) -> str:
    dia = "el lunes" if scheduled.weekday() == 0 and now.weekday() in {4, 5, 6} else "mañana"
    return f"Te parece que lo enviemos {dia} mejor?"


def decide_delivery_time(now: datetime, allow_out_of_hours: bool = False) -> DeliveryDecision:
    in_workday = now.weekday() in WORK_DAYS
    in_worktime = WORK_START_HOUR <= now.hour < WORK_END_HOUR

    if allow_out_of_hours:
        return DeliveryDecision(True, None, "envio_forzado_fuera_de_horario", False, "", ["enviar_ahora"])

    if in_workday and in_worktime:
        return DeliveryDecision(True, None, "horario_laboral", False, "", ["enviar_ahora"])

    scheduled = _next_business_morning(now)
    suggestion = _build_ooh_suggestion(now, scheduled)
    return DeliveryDecision(
        False,
        scheduled.isoformat(),
        "retener_y_posdatar",
        True,
        suggestion,
        ["enviar_ahora", "programar_manana_o_lunes_manana"],
    )


def build_recipients(base_to: List[str], base_cc: List[str] | None = None, category: str = "general") -> Dict[str, List[str]]:
    cc = set((base_cc or []) + DEFAULT_CC)

    if category == "administrativo":
        cc.update(ADMIN_EXTRA_CC)
    if category == "soporte":
        cc.update(SUPPORT_EXTRA_CC)

    return {
        "to": sorted(set(base_to)),
        "cc": sorted(cc),
        "reply_all": True,
    }


def normalize_subject_for_reply(subject: str) -> str:
    s = (subject or "").strip()
    for prefix in ["FW:", "Fwd:", "RV:", "Re:"]:
        if s.lower().startswith(prefix.lower()):
            s = s[len(prefix):].strip()
    return s


def build_internal_forward_intro(requester_name: str, topic: str) -> str:
    req = (requester_name or "el equipo interno").strip()
    t = (topic or "este tema").strip()
    return (
        f"Buenas, soy Laia. {req} me pidió que diera seguimiento a {t} "
        f"y se le dará prioridad para avanzar de forma ordenada."
    )


def build_errata_message(corrected_summary: str) -> str:
    summary = (corrected_summary or "la información corregida").strip()
    return (
        "Buenas,\n\n"
        "Disculpen el mensaje anterior. Estamos trabajando con un nuevo sistema de gestión con IA "
        "y en este caso la tecnología nos jugó una mala pasada.\n\n"
        f"Compartimos a continuación {summary}.\n\n"
        "Saludos,\n"
        "Laia"
    )


def build_recovery_protocol_note() -> Dict[str, Any]:
    return {
        "can_recall_after_send": False,
        "rule": "Una vez entregado por SMTP no hay retiro garantizado. Actuar con fe de erratas.",
        "actions": [
            "detectar error",
            "bloquear nuevos envíos del hilo",
            "enviar fe de erratas por reply-all",
            "mantener copia a dario@grid-code.tech",
            "si administrativo agregar lorena@grid-code.tech",
            "si soporte agregar support@grid-code.tech",
        ],
    }
