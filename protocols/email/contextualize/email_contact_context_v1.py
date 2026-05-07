from typing import Dict, Any, List

PROTOCOL_ID = "email_contact_context_v1"


def _domain(email: str) -> str:
    if not email or "@" not in email:
        return ""
    return email.split("@", 1)[1].lower().strip()


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contextualiza un mail por remitente + historial de contacto.

    Inputs esperados:
      - email: {from, subject, body, thread_id, cc[]}
      - contact_history: lista de interacciones previas del remitente
      - known_contacts: lista de contactos existentes
      - gridcode_domains: lista de dominios internos (default: grid-code.tech)

    Salida:
      - first_mail_in_thread
      - known_sender
      - relation_detected
      - context_level (none|minimal|expanded)
      - tone_hint (formal|neutral|fresh)
      - last_3_topics
      - contact_update_suggested
      - pending_only_candidate
    """
    email = inputs.get("email", {}) or {}
    sender = _normalize(email.get("from", ""))
    sender_domain = _domain(sender)
    subject = (email.get("subject", "") or "").strip()

    grid_domains = [_normalize(d) for d in (inputs.get("gridcode_domains") or ["grid-code.tech"]) if d]
    known_contacts: List[Dict[str, Any]] = inputs.get("known_contacts", []) or []
    history: List[Dict[str, Any]] = inputs.get("contact_history", []) or []

    # 1) Remitente conocido
    sender_contact = next((c for c in known_contacts if _normalize(c.get("email", "")) == sender), None)
    known_sender = sender_contact is not None

    # 2) Primer mail del hilo
    first_mail_in_thread = len(history) == 0

    # 3) Relación detectada (aunque asunto nuevo)
    relation_detected = known_sender or len(history) > 0

    # 4) Participación Grid Code en el email
    cc_list = [(_normalize(x)) for x in (email.get("cc", []) or [])]
    participants = [sender] + cc_list
    has_gridcode_participant = any(_domain(p) in grid_domains for p in participants if p)

    # 5) Estilo sugerido por comportamiento previo
    formal_votes = 0
    fresh_votes = 0
    for h in history[-10:]:
        tone = _normalize(h.get("tone", ""))
        if tone in ("formal", "very_formal"):
            formal_votes += 1
        if tone in ("informal", "fresh"):
            fresh_votes += 1

    if formal_votes > fresh_votes and formal_votes >= 2:
        tone_hint = "formal"
    elif fresh_votes > formal_votes and fresh_votes >= 2:
        tone_hint = "fresh"
    else:
        tone_hint = "neutral"

    # 6) Últimos 3 temas
    topics = []
    for h in reversed(history):
        t = (h.get("topic") or "").strip()
        if t and t not in topics:
            topics.append(t)
        if len(topics) == 3:
            break

    # 7) Nivel de contexto
    if relation_detected and len(topics) > 0:
        context_level = "expanded"
    elif relation_detected:
        context_level = "minimal"
    else:
        context_level = "none"

    # 8) Sugerencia de update de contacto
    contact_update_suggested = known_sender or has_gridcode_participant or relation_detected

    # 9) Candidato a cola pendiente
    status = _normalize(email.get("status", "pending"))
    pending_only_candidate = status in ("pending", "open", "awaiting_reply")

    return {
        "protocol_id": PROTOCOL_ID,
        "sender": sender,
        "sender_domain": sender_domain,
        "subject": subject,
        "first_mail_in_thread": first_mail_in_thread,
        "known_sender": known_sender,
        "relation_detected": relation_detected,
        "has_gridcode_participant": has_gridcode_participant,
        "context_level": context_level,
        "tone_hint": tone_hint,
        "last_3_topics": topics,
        "contact_update_suggested": contact_update_suggested,
        "pending_only_candidate": pending_only_candidate,
    }
