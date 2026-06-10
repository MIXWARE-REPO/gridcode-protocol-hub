from __future__ import annotations

from typing import Any, Dict

from shared.orchestration.internal_capability_catalog_v1 import build_internal_capabilities_block

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
    include_capabilities = bool(inputs.get("include_internal_capabilities", False))
    recipient_email = inputs.get("recipient_email", inputs.get("to_email", "laia@grid-code.tech"))

    body = _base_body(name, context, next_step)
    internal_capabilities = None

    if include_capabilities:
        block = build_internal_capabilities_block(name=name or "Laia", to_email=recipient_email)
        internal_capabilities = block
        body = f"{body}\n\n{block['text']}"

    return {
        "protocol_id": PROTOCOL_ID,
        "body": body,
        "internal_capabilities": internal_capabilities,
    }
