from typing import Dict, Any

PROTOCOL_ID = "email_interpret_v1"

KEYWORDS_TICKET = ["ticket", "gc-ev-", "incidencia", "error", "falla"]
KEYWORDS_COMMERCIAL = ["presupuesto", "cotizacion", "demo", "comercial"]

def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    subject = (inputs.get("subject") or "").lower()
    body = (inputs.get("body") or "").lower()
    text = f"{subject} {body}"

    if any(k in text for k in KEYWORDS_TICKET):
        category = "ticket"
        priority = "high" if "caido" in text or "no carga" in text else "medium"
    elif any(k in text for k in KEYWORDS_COMMERCIAL):
        category = "commercial"
        priority = "medium"
    else:
        category = "general"
        priority = "low"

    return {
        "protocol_id": PROTOCOL_ID,
        "category": category,
        "priority": priority,
        "requires_reply": True,
    }
