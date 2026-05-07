from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Any


FlowState = Literal["OK", "PARCIAL", "INCONSISTENTE", "SIN_EVIDENCIA"]
HealthBand = Literal["SANO", "SEGUIMIENTO ACTIVO", "ATENCIÓN ALTA", "PRIORIDAD MÁXIMA"]

FLOW_STAGES = [
    "acceso_remoto",
    "backend",
    "boot_reinicios",
    "autorizacion",
    "inicio_sesion",
    "continuidad",
    "cierre_sesion",
]

ACTIVITY_TYPES = [
    "Carga registrada",
    "Carga con anomalía",
    "Sin carga registrada",
    "Sin evidencia suficiente",
]


@dataclass
class RemotePolicyValidationResult:
    ok: bool
    errors: List[str] = field(default_factory=list)


@dataclass
class RemoteMetrics:
    sesiones_totales: int
    sesiones_exitosas: int
    cargas_fallidas_referidas: int
    interrupciones_sesion: int
    reinicios_detectados: int
    dias_con_actividad: int
    dias_sin_actividad: int
    desconexiones_backend: int
    boot_por_dia: float
    cierres_automaticos: int
    rechazos_auth: int
    sin_cierre_consistente: int


def classify_health_band(efectividad: float) -> HealthBand:
    if efectividad > 70:
        return "SANO"
    if 50 <= efectividad <= 70:
        return "SEGUIMIENTO ACTIVO"
    if 40 <= efectividad < 50:
        return "ATENCIÓN ALTA"
    return "PRIORIDAD MÁXIMA"


def compute_efectividad(sesiones_totales: int, sesiones_exitosas: int) -> float:
    if sesiones_totales <= 0:
        return 0.0
    return round((sesiones_exitosas / sesiones_totales) * 100.0, 2)


def validate_flow_ocpp_shape(flow_ocpp: Dict[str, Any]) -> RemotePolicyValidationResult:
    errors: List[str] = []
    for stage in FLOW_STAGES:
        if stage not in flow_ocpp:
            errors.append(f"missing_flow_stage:{stage}")
            continue
        node = flow_ocpp.get(stage, {})
        state = node.get("estado")
        detail = node.get("detalle")
        if state not in {"OK", "PARCIAL", "INCONSISTENTE", "SIN_EVIDENCIA"}:
            errors.append(f"invalid_state:{stage}")
        if not isinstance(detail, str) or not detail.strip():
            errors.append(f"missing_detail:{stage}")
    return RemotePolicyValidationResult(ok=(len(errors) == 0), errors=errors)


def validate_activity_row(row: Dict[str, Any]) -> RemotePolicyValidationResult:
    errors: List[str] = []
    if row.get("tipo") not in ACTIVITY_TYPES:
        errors.append("invalid_activity_type")
    for k in ["fecha", "dia_semana"]:
        if not str(row.get(k, "")).strip():
            errors.append(f"missing_{k}")
    if not isinstance(row.get("sesiones"), int):
        errors.append("invalid_sesiones")
    if not isinstance(row.get("reinicio"), bool):
        errors.append("invalid_reinicio")
    if not isinstance(row.get("cierre_inconsistente"), bool):
        errors.append("invalid_cierre_inconsistente")
    return RemotePolicyValidationResult(ok=(len(errors) == 0), errors=errors)
