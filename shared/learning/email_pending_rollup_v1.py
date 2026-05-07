from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

LEARNING_LOG_PATH = Path("data/email_learning_log.jsonl")
WEEKLY_OUTPUT_DIR = Path("data/weekly_pending")


def _parse_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def _week_range(ref: datetime) -> tuple[datetime, datetime]:
    start = (ref - timedelta(days=ref.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    return start, end


def _ts(row: Dict[str, Any]) -> datetime | None:
    v = row.get("timestamp")
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except Exception:
        return None


def close_p1_when_answered(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        nr = dict(r)
        if nr.get("priority") == "p1" and nr.get("outcome") == "respondio_ok":
            nr["pending"] = False
        elif nr.get("outcome") in {"sin_respuesta", "pidio_ajuste", "pending"}:
            nr["pending"] = True
        else:
            nr["pending"] = False
        out.append(nr)
    return out


def build_weekly_pending_snapshot(now: datetime | None = None, log_path: str | Path = LEARNING_LOG_PATH, output_dir: str | Path = WEEKLY_OUTPUT_DIR) -> Dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    start, end = _week_range(now)

    rows = _parse_jsonl(Path(log_path))
    rows = close_p1_when_answered(rows)

    weekly = []
    for r in rows:
        t = _ts(r)
        if not t:
            continue
        if start <= t < end and r.get("pending") is True:
            weekly.append(r)

    payload = {
        "generated_at": now.replace(microsecond=0).isoformat(),
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "pending_count": len(weekly),
        "items": weekly,
    }

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"pending_week_{start.date().isoformat()}.json"
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"saved": True, "path": str(out_file), "payload": payload}


def get_current_pending(log_path: str | Path = LEARNING_LOG_PATH) -> Dict[str, Any]:
    rows = close_p1_when_answered(_parse_jsonl(Path(log_path)))
    pending = [r for r in rows if r.get("pending") is True]
    return {"pending_count": len(pending), "items": pending}
