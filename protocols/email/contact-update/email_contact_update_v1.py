from typing import Dict, Any, List
from datetime import datetime, timezone

PROTOCOL_ID = "email_contact_update_v1"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uniq_keep_order(items: List[str]) -> List[str]:
    out = []
    seen = set()
    for i in items:
        key = (i or "").strip()
        if not key:
            continue
        if key.lower() in seen:
            continue
        seen.add(key.lower())
        out.append(key)
    return out


def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Protocolo de actualización de contacto para email.

    Objetivo:
    - Decidir si actualizar Google Contacts.
    - Construir payload estandarizado para update/insert.
    - Mantener contexto vivo: tono, últimos temas, estado de relación.

    Entradas clave:
    - contact: ficha actual (puede venir vacía si no existe)
    - context: salida del protocolo email_contact_context_v1
    - email: datos del correo actual
    - policy: límites (ej: max_topics=3)

    Salidas:
    - action: create|minimal_update|full_update|skip
    - update_payload: campos a persistir
    - reason_codes: por qué se decidió esa acción
    """
    contact = inputs.get("contact") or {}
    context = inputs.get("context") or {}
    email = inputs.get("email") or {}
    policy = inputs.get("policy") or {}

    max_topics = int(policy.get("max_topics", 3) or 3)
    sender = (context.get("sender") or email.get("from") or "").strip().lower()

    known_sender = bool(context.get("known_sender", False))
    relation_detected = bool(context.get("relation_detected", False))
    context_level = (context.get("context_level") or "none").strip().lower()
    tone_hint = (context.get("tone_hint") or "neutral").strip().lower()
    suggested = bool(context.get("contact_update_suggested", False))

    existing_topics = contact.get("last_topics") or []
    new_topics = context.get("last_3_topics") or []
    merged_topics = _uniq_keep_order(list(new_topics) + list(existing_topics))[:max_topics]

    reason_codes = []

    if not suggested:
        action = "skip"
        reason_codes.append("no_update_suggested")
    elif not contact:
        action = "create"
        reason_codes.append("contact_not_found")
    elif context_level == "expanded" or relation_detected:
        action = "full_update"
        reason_codes.append("relation_or_expanded_context")
    elif known_sender:
        action = "minimal_update"
        reason_codes.append("known_sender_minimal_context")
    else:
        action = "skip"
        reason_codes.append("insufficient_context")

    is_cc_only = bool(email.get("is_cc_only", False))
    if is_cc_only and action in ("create", "full_update"):
        action = "minimal_update" if contact else "create"
        reason_codes.append("cc_only_downgrade")

    update_payload = {
        "email": sender,
        "last_contact_at": _now_iso(),
        "tone_profile": tone_hint,
        "context_level": context_level,
        "last_topics": merged_topics,
        "relationship_active": bool(relation_detected or known_sender),
        "pending_state": (email.get("status") or "pending").strip().lower(),
    }

    if action == "minimal_update":
        update_payload = {
            "email": sender,
            "last_contact_at": update_payload["last_contact_at"],
            "pending_state": update_payload["pending_state"],
        }

    if action == "skip":
        update_payload = {}

    return {
        "protocol_id": PROTOCOL_ID,
        "action": action,
        "reason_codes": reason_codes,
        "update_payload": update_payload,
        "expected_store": "google_contacts",
    }
