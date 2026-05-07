from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

from shared.policies.ocpp_report_infranqueable_policy_v1 import classify_evaluation, health_band, nd


@dataclass
class OcppEvent:
    ts: datetime
    message_type: str
    payload: Dict[str, Any]


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def extract_boot_metadata(events: List[OcppEvent]) -> Dict[str, str]:
    # toma el BootNotification más reciente dentro de ventana
    boots = [e for e in events if e.message_type == "BootNotification"]
    if not boots:
        return {"serial_number": "N/D en log", "firmware": "N/D en log", "ocpp_version": "OCPP 1.6J"}

    payload = boots[-1].payload or {}
    return {
        "serial_number": nd(payload.get("chargePointSerialNumber") or payload.get("serialNumber")),
        "firmware": nd(payload.get("firmwareVersion")),
        "ocpp_version": nd(payload.get("ocppVersion") or "OCPP 1.6J"),
    }


def build_daily_window(start: datetime, end: datetime) -> List[datetime]:
    days = []
    d = start.replace(hour=0, minute=0, second=0, microsecond=0)
    while d.date() <= end.date():
        days.append(d)
        d = d + timedelta(days=1)
    return days


def analyze(metadata: Dict[str, Any], events_raw: List[Dict[str, Any]]) -> Dict[str, Any]:
    events = [OcppEvent(ts=parse_iso(x["timestamp"]), message_type=x.get("message_type", ""), payload=x.get("payload", {}) or {}) for x in events_raw]
    events.sort(key=lambda x: x.ts)

    ws = parse_iso(metadata["window_start"])
    we = parse_iso(metadata["window_end"])
    window_events = [e for e in events if ws <= e.ts <= we]

    boot_meta = extract_boot_metadata(window_events)

    # sesiones simplificadas
    starts = [e for e in window_events if e.message_type in {"StartTransaction", "TransactionEvent.Start"}]
    stops = [e for e in window_events if e.message_type in {"StopTransaction", "TransactionEvent.End"}]
    sessions_total = len(starts)
    sessions_success = min(len(starts), len(stops))

    incomplete = max(0, sessions_total - sessions_success)
    recurrent_incomplete = incomplete >= 2

    auth_rejects = 0
    for e in window_events:
        if e.message_type in {"Authorize", "TransactionEvent.Auth"}:
            st = str((e.payload or {}).get("status") or (e.payload or {}).get("idTagInfo", {}).get("status") or "")
            if st.lower() in {"invalid", "rejected", "blocked", "expired"}:
                auth_rejects += 1

    structural_failure = auth_rejects >= 2

    efectividad = round((sessions_success / sessions_total) * 100, 2) if sessions_total > 0 else 0.0
    evaluacion = classify_evaluation(efectividad, recurrent_incomplete, structural_failure)
    banda = health_band(efectividad)

    day_map = defaultdict(list)
    for e in window_events:
        day_map[e.ts.date().isoformat()].append(e)

    timeline = []
    for d in build_daily_window(ws, we):
        rows = day_map.get(d.date().isoformat(), [])
        day_starts = [x for x in rows if x.message_type in {"StartTransaction", "TransactionEvent.Start"}]
        day_stops = [x for x in rows if x.message_type in {"StopTransaction", "TransactionEvent.End"}]
        if len(day_starts) == 0:
            tipo = "Sin carga registrada"
            count = None
        elif len(day_stops) >= len(day_starts):
            tipo = "Carga registrada"
            count = len(day_starts)
        else:
            tipo = "Carga con anomalía"
            count = len(day_starts)
        timeline.append({
            "date": d.strftime("%d %b"),
            "dow": d.strftime("%a").capitalize(),
            "tipo": tipo,
            "count": count,
        })

    if evaluacion == "BIEN":
        accion = "Operación normal; mantener monitoreo remoto estándar."
    elif evaluacion == "REGULAR":
        accion = "Seguimiento activo remoto con pruebas controladas adicionales."
    else:
        accion = "Requiere intervención técnica: escalar revisión onsite/backend según hallazgo."

    interpretacion = {
        "BIEN": "Conexión backend estable y sesiones solicitadas completadas. Sin patrón estructural de falla.",
        "REGULAR": "Se observa operación funcional con señales de variabilidad; requiere seguimiento activo.",
        "REQUIERE_INTERVENCION": "La evidencia muestra degradación operativa sostenida o fallas recurrentes; requiere intervención.",
    }[evaluacion]

    return {
        "charger_id": metadata["charger_id"],
        "client": metadata["client"],
        "location": metadata["location"],
        "ticket_id": metadata["ticket_id"],
        "analyst": metadata["analyst"],
        "issued_at": metadata["issued_at"],
        "window_start": metadata["window_start"],
        "window_end": metadata["window_end"],
        "ip": nd(metadata.get("ip")),
        "serial_number": boot_meta["serial_number"],
        "firmware": boot_meta["firmware"],
        "ocpp_version": boot_meta["ocpp_version"],
        "efectividad": efectividad,
        "banda": banda,
        "evaluacion": evaluacion,
        "timeline": timeline,
        "sessions_total": sessions_total,
        "sessions_success": sessions_success,
        "incomplete": incomplete,
        "auth_rejects": auth_rejects,
        "interpretacion": interpretacion,
        "accion": accion,
    }
