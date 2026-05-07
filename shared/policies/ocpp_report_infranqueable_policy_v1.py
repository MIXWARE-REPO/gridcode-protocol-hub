from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Evaluation = Literal["BIEN", "REGULAR", "REQUIERE_INTERVENCION"]


def classify_evaluation(efectividad: float, recurrent_incomplete: bool, structural_failure: bool) -> Evaluation:
    if structural_failure or efectividad < 50:
        return "REQUIERE_INTERVENCION"
    if 50 <= efectividad < 80 or recurrent_incomplete:
        return "REGULAR"
    return "BIEN"


def health_band(efectividad: float) -> str:
    if efectividad > 70:
        return "SANO"
    if 50 <= efectividad <= 70:
        return "SEGUIMIENTO ACTIVO"
    if 40 <= efectividad < 50:
        return "ATENCIÓN ALTA"
    return "PRIORIDAD MÁXIMA"


def nd(value: str | None) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "N/D en log"
