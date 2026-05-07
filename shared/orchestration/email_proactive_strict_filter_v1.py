from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from shared.policies.email_priority_policy_v1 import classify_priority

NOISE_KEYWORDS = {
    "instagram", "newsletter", "promoción", "promocion", "sale", "oferta",
    "social", "linkedin", "facebook", "x.com", "twitter", "youtube",
}


@dataclass
class RelevantMail:
    sender: str
    subject: str
    priority: str  # P1|P2
    reason: str
    suggested_action: str


def _is_noise(subject: str, sender: str) -> bool:
    s = f"{subject} {sender}".lower()
    return any(k in s for k in NOISE_KEYWORDS)


def is_relevant(mail: Dict[str, Any]) -> bool:
    subject = str(mail.get("subject", ""))
    sender = str(mail.get("sender", ""))

    if _is_noise(subject, sender):
        return False

    priority = classify_priority(mail.get("to", []), mail.get("cc", []))
    if priority is None:
        return False

    # Señal mínima: no leído o actualizado recientemente
    unread = bool(mail.get("unread", False))
    updated = bool(mail.get("updated_recently", False))
    return unread or updated


def build_relevant_summary(mail: Dict[str, Any]) -> RelevantMail:
    priority = classify_priority(mail.get("to", []), mail.get("cc", [])) or "P2"
    sender = str(mail.get("sender", "")).strip()
    subject = str(mail.get("subject", "")).strip()

    reason = "Hilo operativo con acción pendiente"
    if priority == "P1":
        reason = "Laia está en TO y requiere respuesta prioritaria"

    action = "Responder en el mismo hilo con siguiente paso claro"
    return RelevantMail(
        sender=sender,
        subject=subject,
        priority=priority,
        reason=reason,
        suggested_action=action,
    )


def filter_relevant_mails(mails: List[Dict[str, Any]]) -> List[RelevantMail]:
    out: List[RelevantMail] = []
    for m in mails:
        if is_relevant(m):
            out.append(build_relevant_summary(m))
    return out
