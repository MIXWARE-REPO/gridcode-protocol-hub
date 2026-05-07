from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class TriggerDecision:
    accepted: bool
    reason: str
    dedupe_key: str
    event_type: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def compute_dedupe_key(payload: Dict[str, Any]) -> str:
    raw = "|".join(
        [
            str(payload.get("provider", "")),
            str(payload.get("account", "")),
            str(payload.get("message_id", "")),
            str(payload.get("thread_id", "")),
            str(payload.get("event_ts", "")),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    calc = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(calc, (signature or "").strip())


def validate_payload(payload: Dict[str, Any]) -> tuple[bool, str]:
    required = ["provider", "account", "event_type", "message_id", "thread_id", "event_ts"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        return False, f"missing_fields:{','.join(missing)}"

    if payload.get("event_type") not in {"new_message", "thread_update", "message_updated"}:
        return False, "unsupported_event_type"

    return True, "ok"


def evaluate_trigger(payload: Dict[str, Any], seen_keys: set[str] | None = None) -> TriggerDecision:
    ok, reason = validate_payload(payload)
    dedupe_key = compute_dedupe_key(payload)

    if not ok:
        return TriggerDecision(False, reason, dedupe_key, str(payload.get("event_type", "unknown")))

    seen_keys = seen_keys or set()
    if dedupe_key in seen_keys:
        return TriggerDecision(False, "duplicate_event", dedupe_key, str(payload.get("event_type", "unknown")))

    return TriggerDecision(True, "accepted", dedupe_key, str(payload.get("event_type", "unknown")))


def build_inbound_update_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evento canónico para disparar el rail de email.
    """
    return {
        "protocol": "email_webhook_trigger_v1",
        "received_at": _now_iso(),
        "provider": payload.get("provider"),
        "account": payload.get("account"),
        "event_type": payload.get("event_type"),
        "message": {
            "message_id": payload.get("message_id"),
            "thread_id": payload.get("thread_id"),
            "from": payload.get("from"),
            "to": payload.get("to", []),
            "cc": payload.get("cc", []),
            "subject": payload.get("subject", ""),
            "snippet": payload.get("snippet", ""),
            "labels": payload.get("labels", []),
            "has_attachments": bool(payload.get("has_attachments", False)),
        },
        "routing_hint": {
            "start_pipeline": True,
            "pipeline": "protocols/email/pipeline_email_v1.py",
        },
    }


def parse_raw_event(raw_body: bytes) -> Dict[str, Any]:
    return json.loads(raw_body.decode("utf-8"))
