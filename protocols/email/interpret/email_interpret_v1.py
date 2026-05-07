from typing import Dict, Any

PROTOCOL_ID = "email_interpret_v1"

KEYWORDS_TICKET = ["ticket", "gc-ev-", "incidencia", "error", "falla"]
KEYWORDS_COMMERCIAL = ["presupuesto", "cotizacion", "demo", "comercial"]


def _to_text(value: Any) -> str:
    return (value or "").lower()


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [_to_text(v).strip() for v in value if str(v).strip()]
    return [_to_text(value).strip()]


def _topic_from_subject(subject: str) -> str:
    clean = " ".join(subject.replace("fwd:", "").replace("re:", "").split()).strip()
    return clean[:120] if clean else "tema en seguimiento"


def _build_p2_notification(topic: str) -> str:
    return f"Nos llegó un mail por {topic}; cualquier cosa nos dice."


def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reglas de negocio (Dario):
    - Todo mail entrante se trata como ticket.
    - Si Laia está en TO (destinataria directa): prioridad 1, requiere respuesta.
    - Si Laia está en CC: prioridad 2, informar/monitorear (normalmente responde Dario).
    - Reenvíos: menor prioridad relativa.
    - Para P2, generar aviso de 1 línea con tópico (sin desarrollo largo).
    """
    subject = _to_text(inputs.get("subject"))
    body = _to_text(inputs.get("body"))
    text = f"{subject} {body}"

    to_list = _as_list(inputs.get("to"))
    cc_list = _as_list(inputs.get("cc"))
    laia_email = _to_text(inputs.get("laia_email") or "laia@grid-code.tech")
    is_forward = bool(inputs.get("is_forward", False))

    laia_in_to = laia_email in to_list
    laia_in_cc = laia_email in cc_list and not laia_in_to

    category = "ticket"
    technical_urgency = ("caido" in text) or ("no carga" in text) or any(k in text for k in KEYWORDS_TICKET)

    if laia_in_to:
        priority = "p1"
        requires_reply = True
        action = "reply_required"
    elif laia_in_cc:
        priority = "p2"
        requires_reply = False
        action = "notify_dario_watch"
    else:
        priority = "p2"
        requires_reply = False
        action = "watch"

    if is_forward and priority == "p2":
        action = "watch_forward"

    topic = _topic_from_subject(subject)
    p2_notification = _build_p2_notification(topic) if priority == "p2" else ""

    sender = (inputs.get("from_name") or inputs.get("from") or "cliente").strip()
    p1_assist_message = ""
    if priority == "p1":
        p1_assist_message = f"Me llegó un mail de {sender} con un requerimiento por {topic}; está esperando respuesta. ¿Qué enfoque le damos?"

    return {
        "protocol_id": PROTOCOL_ID,
        "category": category,
        "priority": priority,
        "requires_reply": requires_reply,
        "action": action,
        "laia_in_to": laia_in_to,
        "laia_in_cc": laia_in_cc,
        "is_forward": is_forward,
        "technical_urgency": technical_urgency,
        "topic": topic,
        "p2_notification": p2_notification,
        "p1_assist_message": p1_assist_message,
    }
