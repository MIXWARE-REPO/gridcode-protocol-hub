from typing import Dict, Any, List

PROTOCOL_ID = "email_read_v1"

def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    emails: List[Dict[str, Any]] = inputs.get("emails", [])
    normalized = []
    for e in emails:
        normalized.append({
            "id": str(e.get("id", "")),
            "from": e.get("from", ""),
            "from_name": e.get("from_name", ""),
            "to": e.get("to", []),
            "cc": e.get("cc", []),
            "subject": e.get("subject", ""),
            "body": e.get("body", ""),
            "timestamp": e.get("timestamp", ""),
            "is_read": bool(e.get("is_read", False)),
            "thread_id": e.get("thread_id", ""),
            "is_forward": bool(e.get("is_forward", False))
        })
    return {"protocol_id": PROTOCOL_ID, "emails": normalized, "count": len(normalized)}
