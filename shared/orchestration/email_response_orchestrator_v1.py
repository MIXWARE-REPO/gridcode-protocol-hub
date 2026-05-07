from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


STYLE_SKILL = "email-style-grid-code"


@dataclass
class ProactiveTask:
    due_at: str
    title: str
    detail: str
    reason: str
    assignee: str = "dario@grid-code.tech"
    source: str = "email"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _due_iso_for_slot(days_ahead: int, slot: str) -> str:
    now = datetime.now(timezone.utc)
    hour = 10 if (slot or "manana") == "manana" else 16
    dt = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=0, second=0, microsecond=0)
    return dt.isoformat()


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def detect_commitments(user_instruction: str, draft_body: str, preferred_slot: str = "manana") -> List[Dict[str, Any]]:
    text = f"{_normalize(user_instruction)} {_normalize(draft_body)}"
    commitments: List[Dict[str, Any]] = []

    if any(k in text for k in ["mañana", "manana", "tomorrow"]):
        commitments.append({
            "type": "followup_tomorrow",
            "label": "Compromiso de seguimiento para mañana",
            "due_at": _due_iso_for_slot(1, preferred_slot),
            "preferred_slot": preferred_slot,
        })

    if any(k in text for k in ["semana próxima", "semana proxima", "la semana que viene"]):
        commitments.append({
            "type": "followup_next_week",
            "label": "Compromiso de seguimiento para la semana próxima",
            "due_at": _due_iso_for_slot(7, preferred_slot),
            "preferred_slot": preferred_slot,
        })

    return commitments


def build_proactive_tasks(commitments: List[Dict[str, Any]], topic: str, contact_name: str, assignee_email: str = "dario@grid-code.tech") -> List[ProactiveTask]:
    tasks: List[ProactiveTask] = []
    safe_topic = (topic or "tema de email").strip()
    safe_contact = (contact_name or "cliente").strip()

    for c in commitments:
        tasks.append(
            ProactiveTask(
                due_at=c["due_at"],
                title=f"Seguimiento email: {safe_topic}",
                detail=f"Revisar con Dario el tema de {safe_contact} y definir respuesta/acción.",
                reason=c["label"],
                assignee=assignee_email,
                source="email",
            )
        )
    return tasks


def apply_style_guardrails(draft_body: str) -> Dict[str, Any]:
    body = (draft_body or "").strip()
    errors: List[str] = []

    if not body.lower().startswith("buenas"):
        errors.append("La respuesta debe iniciar con 'Buenas'.")

    banned = ["ahora mismo", "inmediatamente", "te comento", "contigo", "tuyo", "tuya"]
    for b in banned:
        if b in body.lower():
            errors.append(f"Contiene frase no permitida: '{b}'.")

    if "\n\n" not in body:
        errors.append("Debe tener separación en párrafos (línea en blanco).")

    if not body.endswith("Saludos,\nLaia"):
        errors.append("Debe cerrar con firma exacta: 'Saludos,\\nLaia'.")

    return {"valid": len(errors) == 0, "errors": errors, "style_skill": STYLE_SKILL}


def build_confirmation_block(
    to_email: str,
    subject: str,
    final_body: str,
    commitments: List[Dict[str, Any]],
    proactive_tasks: List[ProactiveTask],
) -> Dict[str, Any]:
    return {
        "generated_at": _now_iso(),
        "to": to_email,
        "subject": subject,
        "final_body": final_body,
        "commitments": commitments,
        "proactive_tasks": [t.__dict__ for t in proactive_tasks],
        "summary": {
            "has_commitments": len(commitments) > 0,
            "tasks_to_schedule": len(proactive_tasks),
        },
    }


def build_google_task_payloads(tasks: List[ProactiveTask]) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    for t in tasks:
        payloads.append(
            {
                "title": t.title,
                "notes": f"{t.detail}\nMotivo: {t.reason}\nAsignado: {t.assignee}",
                "due": t.due_at,
                "assignee": t.assignee,
                "source": t.source,
            }
        )
    return payloads


def orchestrate_email_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entrada esperada:
    - instruction: frase de Dario (ej. 'contestale que lo recibimos...')
    - topic
    - contact_name
    - to_email
    - subject
    - final_body (ya contextualizado y redactado)

    Salida:
    - bloque de confirmación proactiva
    - detección de compromisos
    - tareas sugeridas para agenda/seguimiento
    - validación de estilo base
    """
    instruction = payload.get("instruction", "")
    topic = payload.get("topic", "tema en seguimiento")
    contact_name = payload.get("contact_name", "cliente")
    to_email = payload.get("to_email", "")
    subject = payload.get("subject", "")
    final_body = payload.get("final_body", "")
    preferred_slot = payload.get("preferred_slot", "manana")  # manana|tarde
    assignee_email = payload.get("assignee_email", "dario@grid-code.tech")

    commitments = detect_commitments(instruction, final_body, preferred_slot=preferred_slot)
    tasks = build_proactive_tasks(commitments, topic, contact_name, assignee_email=assignee_email)
    style = apply_style_guardrails(final_body)
    confirm = build_confirmation_block(to_email, subject, final_body, commitments, tasks)

    return {
        "protocol": "email_response_orchestrator_v1",
        "style_validation": style,
        "confirmation": confirm,
        "task_creation": {
            "provider": "google_tasks",
            "needs_user_slot_confirmation": len(commitments) > 0,
            "slot_options": ["manana", "tarde"],
            "recommended_slot": preferred_slot,
            "payloads": build_google_task_payloads(tasks),
        },
    }
