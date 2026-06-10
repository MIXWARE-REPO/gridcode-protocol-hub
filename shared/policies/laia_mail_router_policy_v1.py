from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List
import re

from shared.orchestration.email_delivery_policy_v1 import (
    build_recipients,
    decide_delivery_time,
    normalize_subject_for_reply,
)
from shared.policies.email_priority_policy_v1 import classify_priority

PROTOCOL_ID = "laia_mail_router_v1"
LAIA_EMAIL = "laia@grid-code.tech"

INTERNAL_DOMAINS = {
    "grid-code.tech",
    "centual.eu",
    "fundacionnovacore.org",
    "mix-ware.com",
}

NOISE_KEYWORDS = {"newsletter", "promoción", "promocion", "sale", "oferta", "unsubscribe", "linkedin", "instagram", "twitter", "x.com", "youtube"}
MEETING_KEYWORDS = {"meet", "meeting", "reunión", "reunion", "agenda", "convocatoria", "calendar"}
DRIVE_KEYWORDS = {"drive", "compartir", "share", "carpeta", "documento", "documentos", "buscar archivo", "archivo"}
REPORT_KEYWORDS = {"informe", "reporte", "report", "resumen", "analisis", "análisis", "preliminar"}
CERTIFICATE_KEYWORDS = {"certificado", "certificate", "constancia", "emisión", "emision"}
CONTACT_KEYWORDS = {"contacto", "firma", "tarjeta", "linkedin", "teléfono", "telefono", "email signature"}
REPLY_KEYWORDS = {"responde", "responder", "contesta", "contestar", "reply"}
ORDER_KEYWORDS = {"haz", "hacer", "ejecuta", "ejecutar", "agenda", "prepara", "revisa", "envía", "enviar", "manda", "mandar", "actualiza", "actualizar", "cambia", "cambiar"}
INFO_KEYWORDS = {"qué", "que", "estado", "status", "confirma", "confirmar", "dime", "decime", "consulta"}
APPROVAL_KEYWORDS = {"apruebas", "aprobar", "confirmas", "confirmar", "ok", "vale", "mandalo", "mándalo", "autorizas", "autorizar"}
COMMITMENT_KEYWORDS = {"mañana", "manana", "semana próxima", "semana proxima", "deadline", "plazo", "entrega", "compromiso"}
CRITICAL_KEYWORDS = {"borrar", "eliminar", "permiso", "credentials", "credenciales", "pagar", "pago", "legal", "contrato", "financiero"}
ADMIN_KEYWORDS = {"factura", "iva", "contable", "administrativo", "gasto", "proveedor", "pago"}
SUPPORT_KEYWORDS = {"soporte", "error", "fallo", "incidencia", "problema", "caido", "caído"}

TARGET_BY_TOPIC = {
    "MEETING": "calendar-meet-host-gridcode",
    "DRIVE": "gridcode-drive-api-first-governance",
    "REPORT": "gridcode-preliminary-analysis-report",
    "CERTIFICATE": "certificate-generation",
    "CONTACT": "mail-contact-update",
    "REPLY": "mail-reply-operational",
    "GENERAL": "mail-reply-operational",
}


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _lower(value: Any) -> str:
    return _clean(value).lower()


def _listify(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [_lower(v) for v in value if _clean(v)]
    if isinstance(value, tuple):
        return [_lower(v) for v in value if _clean(v)]
    if isinstance(value, str):
        return [x.strip().lower() for x in value.split(",") if x.strip()]
    return [_lower(value)]


def _email_domain(email: str) -> str:
    email = _lower(email)
    if "@" not in email:
        return ""
    return email.split("@", 1)[1]


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    return any(k.lower() in text for k in keywords)


def classify_thread_type(from_email: str, to_list: List[str], cc_list: List[str]) -> str:
    participants = [from_email] + list(to_list) + list(cc_list)
    domains = {_email_domain(x) for x in participants if _email_domain(x)}
    if domains and domains.issubset(INTERNAL_DOMAINS):
        return "INTERNAL_ONLY"
    if domains & INTERNAL_DOMAINS and domains - INTERNAL_DOMAINS:
        return "HYBRID_THREAD"
    return "EXTERNAL_ONLY"


def classify_topic(text: str) -> str:
    if _contains_any(text, MEETING_KEYWORDS):
        return "MEETING"
    if _contains_any(text, DRIVE_KEYWORDS):
        return "DRIVE"
    if _contains_any(text, REPORT_KEYWORDS):
        return "REPORT"
    if _contains_any(text, CERTIFICATE_KEYWORDS):
        return "CERTIFICATE"
    if _contains_any(text, CONTACT_KEYWORDS):
        return "CONTACT"
    if _contains_any(text, REPLY_KEYWORDS):
        return "REPLY"
    return "GENERAL"


def classify_intent(text: str) -> str:
    if _contains_any(text, NOISE_KEYWORDS):
        return "SPAM_NOISE"
    if _contains_any(text, APPROVAL_KEYWORDS):
        return "APPROVAL"
    if _contains_any(text, COMMITMENT_KEYWORDS):
        return "COMMITMENT"
    if _contains_any(text, INFO_KEYWORDS):
        return "REQUEST_INFO"
    if _contains_any(text, ORDER_KEYWORDS):
        return "ORDER"
    return "FYI" if text else "UNKNOWN"


def classify_role(actor_role: Any, domain: str) -> str:
    role = _clean(actor_role).upper()
    if role:
        return role
    return "STAFF" if domain in INTERNAL_DOMAINS else "EXTERNAL"


def _mail_category(text: str) -> str:
    if _contains_any(text, ADMIN_KEYWORDS):
        return "administrativo"
    if _contains_any(text, SUPPORT_KEYWORDS):
        return "soporte"
    return "general"


def resolve_target_skill(topic: str, intent: str) -> str:
    if intent == "SPAM_NOISE":
        return "mail-triage"
    return TARGET_BY_TOPIC.get(topic, "mail-reply-operational")


def assess_risk(intent: str, topic: str, thread_type: str, text: str) -> str:
    if _contains_any(text, CRITICAL_KEYWORDS):
        return "CRITICAL"
    if topic == "CERTIFICATE":
        return "HIGH"
    if thread_type == "HYBRID_THREAD":
        return "HIGH" if intent in {"ORDER", "APPROVAL", "COMMITMENT"} else "MEDIUM"
    if thread_type == "EXTERNAL_ONLY":
        return "HIGH" if intent in {"ORDER", "APPROVAL", "COMMITMENT"} else "MEDIUM"
    if intent in {"ORDER", "APPROVAL", "COMMITMENT"}:
        return "MEDIUM"
    if intent == "REQUEST_INFO":
        return "LOW"
    return "LOW"


def determine_action(intent: str, thread_type: str, is_authorized: bool, risk: str) -> str:
    if intent == "SPAM_NOISE":
        return "SILENT"
    if intent == "UNKNOWN":
        return "ESCALATE" if not is_authorized else "DRAFT"
    if risk == "CRITICAL":
        return "REJECT"
    if intent == "APPROVAL":
        return "REQUIRE_APPROVAL"
    if thread_type == "INTERNAL_ONLY" and is_authorized:
        return "EXECUTE" if risk in {"LOW", "MEDIUM"} else "DRAFT"
    if thread_type == "HYBRID_THREAD":
        return "REQUIRE_APPROVAL" if risk in {"HIGH", "CRITICAL"} else "DRAFT"
    if thread_type == "EXTERNAL_ONLY":
        if intent in {"REQUEST_INFO", "FYI"} and risk in {"LOW", "MEDIUM"}:
            return "DRAFT"
        return "REQUIRE_APPROVAL" if risk in {"HIGH", "CRITICAL"} else "ESCALATE"
    if is_authorized and intent in {"ORDER", "REQUEST_INFO", "FYI", "COMMITMENT"}:
        return "EXECUTE" if risk in {"LOW", "MEDIUM"} else "REQUIRE_APPROVAL"
    return "DRAFT"


def _build_reason(intent: str, topic: str, thread_type: str, risk: str, actor_domain: str, action: str, is_authorized: bool) -> str:
    parts = [
        f"dominio={actor_domain or 'unknown'}",
        f"intencion={intent.lower()}",
        f"tema={topic.lower()}",
        f"hilo={thread_type.lower()}",
        f"riesgo={risk.lower()}",
        f"accion={action.lower()}",
    ]
    if not is_authorized:
        parts.append("requiere validación adicional")
    return "; ".join(parts)


def evaluate_mail_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    from_email = _clean(payload.get("from") or payload.get("from_email") or payload.get("sender") or payload.get("actor_email"))
    to_list = _listify(payload.get("to"))
    cc_list = _listify(payload.get("cc"))
    subject = _clean(payload.get("subject"))
    body = _clean(payload.get("body"))
    text = subject + "\n" + body
    actor_domain = _email_domain(from_email)
    thread_type = classify_thread_type(from_email, to_list, cc_list)
    intent = classify_intent(text)
    topic = classify_topic(text)
    category = _mail_category(text)
    target_skill = resolve_target_skill(topic, intent)
    actor_role = classify_role(payload.get("actor_role"), actor_domain)
    allow_senders = {x.lower() for x in _listify(payload.get("authorized_senders"))}
    is_authorized = actor_domain in INTERNAL_DOMAINS or from_email.lower() in allow_senders
    laia_email = _clean(payload.get("laia_email") or LAIA_EMAIL).lower()
    priority = classify_priority(to_list, cc_list, laia_email=laia_email) or "P3"
    risk = assess_risk(intent, topic, thread_type, text)

    confidence = 0.55
    if actor_domain in INTERNAL_DOMAINS:
        confidence += 0.2
    if intent not in {"UNKNOWN", "SPAM_NOISE"}:
        confidence += 0.1
    if topic != "GENERAL":
        confidence += 0.1
    if thread_type == "INTERNAL_ONLY":
        confidence += 0.05
    if thread_type in {"EXTERNAL_ONLY", "HYBRID_THREAD"}:
        confidence -= 0.05
    confidence = max(0.0, min(0.99, confidence))

    now_value = payload.get("now")
    if now_value:
        try:
            now_dt = datetime.fromisoformat(str(now_value))
        except Exception:
            now_dt = datetime.now(timezone.utc)
    else:
        now_dt = datetime.now(timezone.utc)
    delivery = decide_delivery_time(now_dt, allow_out_of_hours=(thread_type == "INTERNAL_ONLY" and risk in {"LOW", "MEDIUM"}))

    action = determine_action(intent, thread_type, is_authorized, risk)
    requires_approval = action == "REQUIRE_APPROVAL"
    if intent == "SPAM_NOISE":
        requires_approval = False
    delay_mode = (
        "NO_DELAY" if action == "SILENT" else
        "BLOCKED" if action == "REJECT" else
        "APPROVAL_DELAY" if requires_approval else
        "NO_DELAY" if delivery.send_now else
        "SHORT_DELAY"
    )

    if action in {"DRAFT", "EXECUTE"} and thread_type == "EXTERNAL_ONLY" and not is_authorized:
        action = "DRAFT" if risk != "CRITICAL" else "ESCALATE"
        requires_approval = False
        delay_mode = "SHORT_DELAY" if action == "DRAFT" else "BLOCKED"

    rules_triggered: List[str] = []
    if actor_domain in INTERNAL_DOMAINS:
        rules_triggered.append("domain_allowlist")
    if priority == "P1":
        rules_triggered.append("priority_p1")
    elif priority == "P2":
        rules_triggered.append("priority_p2")
    if thread_type == "HYBRID_THREAD":
        rules_triggered.append("hybrid_thread_caution")
    if action == "SILENT":
        rules_triggered.append("silence_policy")
    if action == "REQUIRE_APPROVAL":
        rules_triggered.append("approval_gate")
    if risk == "CRITICAL":
        rules_triggered.append("critical_block")

    reply_all = thread_type in {"INTERNAL_ONLY", "HYBRID_THREAD"} and action != "SILENT"
    recipients = build_recipients(base_to=[from_email] if from_email else [], base_cc=cc_list, category=category)
    reply_subject = normalize_subject_for_reply(subject)

    return {
        "protocol_id": PROTOCOL_ID,
        "router": "laia-mail-router",
        "input_channel": _clean(payload.get("channel") or payload.get("input_channel") or "email"),
        "message_id": _clean(payload.get("message_id") or payload.get("id")),
        "thread_id": _clean(payload.get("thread_id") or payload.get("threadId")),
        "actor": {
            "email": from_email,
            "domain": actor_domain,
            "role": actor_role,
            "is_authorized": bool(is_authorized),
        },
        "classification": {
            "intent": intent,
            "topic": topic,
            "thread_type": thread_type,
            "priority": priority,
            "risk": risk,
            "category": category,
            "confidence": round(confidence, 2),
        },
        "routing": {
            "target_skill": target_skill,
            "policy_scope": "mail-router",
            "subskill_path": target_skill,
            "reply_subject": reply_subject,
        },
        "delivery": {
            "send_now": bool(delivery.send_now),
            "scheduled_for": delivery.scheduled_for,
            "mode": "immediate" if delivery.send_now else "retained",
            "is_out_of_hours": bool(delivery.is_out_of_hours),
            "suggestion_message": delivery.suggestion_message,
            "category": category,
        },
        "reply_policy": {
            "reply_all": bool(reply_all),
            "to": recipients["to"],
            "cc": recipients["cc"],
        },
        "decision": {
            "action": action,
            "requires_approval": bool(requires_approval),
            "delay_mode": delay_mode,
            "reason": _build_reason(intent, topic, thread_type, risk, actor_domain, action, is_authorized),
        },
        "audit": {
            "policy_files_consulted": [
                "shared/policies/email_priority_policy_v1.py",
                "shared/orchestration/email_delivery_policy_v1.py",
                "shared/orchestration/email_proactive_strict_filter_v1.py",
                "docs/email-sla-policy.md",
                "docs/email-delivery-and-errata-policy.md",
            ],
            "rules_triggered": rules_triggered,
            "confidence": round(confidence, 2),
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
    }


def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    return evaluate_mail_route(inputs)
