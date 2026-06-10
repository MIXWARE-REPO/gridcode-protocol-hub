from __future__ import annotations

from typing import Any, Dict

from shared.orchestration.internal_capability_catalog_v1 import (
    INTERNAL_MAIL_TO,
    build_internal_capabilities_block,
    build_internal_capabilities_compact_block,
    is_internal_team_email,
)

PROTOCOL_ID = "email_write_v1"


def _base_body(name: str, context: str, next_step: str) -> str:
    greeting = f"Buenas {name}," if name else "Buenas,"
    return (
        f"{greeting}\n\n"
        f"Gracias por el mensaje.\n\n"
        f"En relación con {context}, se estaría revisando la información para darle el tratamiento correspondiente.\n\n"
        f"{next_step}\n\n"
        f"Saludos,\nLaia"
    )


def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    name = inputs.get("name", "") or ""
    context = inputs.get("context", "su consulta")
    next_step = inputs.get("next_step", "Se gestionará con la prioridad correspondiente.")
    include_capabilities = inputs.get("include_internal_capabilities")
    recipient_email = inputs.get("recipient_email", inputs.get("to_email", ""))
    trigger_query = inputs.get("trigger_query", f"{context} {next_step}")
    selected_trigger = inputs.get("selected_trigger")
    capability_mode = (inputs.get("capability_mode") or "compact").strip().lower()

    if include_capabilities is None:
        include_capabilities = bool(recipient_email and is_internal_team_email(recipient_email))
    include_capabilities = bool(include_capabilities)

    body = _base_body(name, context, next_step)
    internal_capabilities = None

    if include_capabilities:
        if capability_mode == "full":
            block = build_internal_capabilities_block(
                name=name or "Laia",
                to_email=INTERNAL_MAIL_TO,
                selected_trigger=selected_trigger,
            )
        else:
            block = build_internal_capabilities_compact_block(
                name=name or "Laia",
                to_email=INTERNAL_MAIL_TO,
                selected_trigger=selected_trigger,
            )
        internal_capabilities = block
        body = f"{body}\n\n{block['text']}"

    return {
        "protocol_id": PROTOCOL_ID,
        "body": body,
        "internal_capabilities": internal_capabilities,
        "trigger_selector": {
            "query": trigger_query,
            "selected_trigger": selected_trigger,
        },
    }
