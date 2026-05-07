from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# Campos de sistema (bloqueados por defecto)
SYSTEM_LOCKED_FIELDS = [
    "ticket_id",
    "visit_date",
    "requester_customer",
    "service_name",
    "charger_label",
    "location",
    "bay_reference",
    "proposed_test_rfid",
    "charger_ip",
    "charger_model_series",
    "intervention_summary",
    "ticket_route_path",
]

CHECKLIST_CONTROLS = [
    "energization",
    "connectivity_ping",
    "physical_state",
    "hose_connector",
    "lock_servo",
    "rfid_reading",
    "authorization_type",
    "session_start",
    "continuity",
    "session_close",
]

STATE_OPTIONS = ["OK", "No OK", "No verificable"]
REQUIRES_ACTION_OPTIONS = ["Sí", "No"]

RESULT_OPTIONS_BY_CONTROL: Dict[str, List[str]] = {
    "energization": ["Normal", "Anómalo", "Sin energía"],
    "connectivity_ping": ["Responde", "Intermitente", "No responde"],
    "physical_state": ["Sin daño visible", "Daño leve", "Daño severo"],
    "hose_connector": ["Operativo", "Falla mecánica", "No detecta"],
    "lock_servo": ["Cierra bien", "No cierra", "Inconsistente"],
    "rfid_reading": ["Lee correcta", "No lee", "Lectura intermitente"],
    "authorization_type": ["Modo libre", "RFID", "App / backend"],
    "session_start": ["Inicia", "No inicia", "Inicia con falla"],
    "continuity": ["Estable", "Se corta", "Inestable"],
    "session_close": ["Cierra bien", "No libera", "Cierre inconsistente"],
}

VISIT_RESULT_OPTIONS = [
    "Operativo OK",
    "Operativo con observaciones",
    "Falla confirmada",
    "Sin visibilidad suficiente",
    "Requiere escalado",
]

DOMINANT_CAUSE_OPTIONS = [
    "Problema local del cargador",
    "Problema de comunicación",
    "Problema de autorización (RFID/backend)",
    "Problema mecánico (manguera/servo/bloqueo)",
    "Externalidad del sitio",
    "No concluyente",
]

NEXT_STEP_OPTIONS = [
    "Cerrar ticket",
    "Seguimiento remoto",
    "Escalar a soporte backend",
    "Programar intervención correctiva",
    "Requiere repuesto",
    "Requiere nueva visita",
]


@dataclass
class OnsiteFormPolicy:
    lock_system_fields: bool = True
    require_checklist_choices: bool = True
    require_open_text_fields: bool = True
    max_open_text_blocks: int = 6
    photo_slots: int = 4
    corporate_header_footer_locked: bool = True
    target_fill_minutes: int = 2


@dataclass
class OnsiteFormValidationResult:
    ok: bool
    errors: List[str] = field(default_factory=list)


def validate_policy_shape() -> OnsiteFormValidationResult:
    errors: List[str] = []

    for control in CHECKLIST_CONTROLS:
        if control not in RESULT_OPTIONS_BY_CONTROL:
            errors.append(f"missing_result_options:{control}")

    if len(STATE_OPTIONS) != 3:
        errors.append("invalid_state_options")

    if len(REQUIRES_ACTION_OPTIONS) != 2:
        errors.append("invalid_requires_action_options")

    if len(VISIT_RESULT_OPTIONS) < 5:
        errors.append("visit_result_options_too_short")

    if len(DOMINANT_CAUSE_OPTIONS) < 6:
        errors.append("dominant_cause_options_too_short")

    if len(NEXT_STEP_OPTIONS) < 6:
        errors.append("next_step_options_too_short")

    return OnsiteFormValidationResult(ok=(len(errors) == 0), errors=errors)
