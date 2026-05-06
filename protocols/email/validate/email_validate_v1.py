from typing import Dict, Any

PROTOCOL_ID = "email_validate_v1"
BANNED = ["/", "{", "}", "ahora mismo", "inmediatamente", "te comento"]


def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    body = inputs.get("body", "")
    errors = []

    if "\n\n" not in body:
        errors.append("missing_paragraph_breaks")
    if not body.strip().endswith("Saludos,\nLaia"):
        errors.append("bad_signature")

    lower = body.lower()
    for b in BANNED:
        if b in lower:
            errors.append(f"banned_token:{b}")

    return {
        "protocol_id": PROTOCOL_ID,
        "valid": len(errors) == 0,
        "errors": errors,
    }
