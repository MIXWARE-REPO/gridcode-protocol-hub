from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

VALID_OUTCOMES = {
    "pending",
    "respondio_ok",
    "sin_respuesta",
    "pidio_ajuste",
    "cerrado_por_otro_canal",
}

DEFAULT_LOG_PATH = Path("data/email_learning_log.jsonl")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _norm_text(value: Any, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def build_learning_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    outcome = _norm_text(payload.get("outcome"), "pending")
    if outcome not in VALID_OUTCOMES:
        outcome = "pending"

    return {
        "timestamp": _now_iso(),
        "channel": "email",
        "priority": _norm_text(payload.get("priority"), "p2"),
        "topic": _norm_text(payload.get("topic"), "tema en seguimiento"),
        "request_summary": _norm_text(payload.get("request_summary"), "sin resumen"),
        "assist_message": _norm_text(payload.get("assist_message")),
        "dario_input": _norm_text(payload.get("dario_input")),
        "final_reply": _norm_text(payload.get("final_reply")),
        "outcome": outcome,
        "improvement_note": _norm_text(payload.get("improvement_note")),
    }


def append_learning_record(payload: Dict[str, Any], log_path: str | Path = DEFAULT_LOG_PATH) -> Dict[str, Any]:
    record = build_learning_record(payload)
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"saved": True, "path": str(path), "record": record}
