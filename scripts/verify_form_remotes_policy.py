#!/usr/bin/env python3
from shared.policies.form_remotes_policy_v1 import (
    compute_efectividad,
    classify_health_band,
    validate_flow_ocpp_shape,
)


def main() -> int:
    ef = compute_efectividad(10, 8)
    print("efectividad", ef)
    print("banda", classify_health_band(ef))

    flow = {
        "acceso_remoto": {"estado": "OK", "detalle": "visibilidad constante"},
        "backend": {"estado": "OK", "detalle": "sin desconexiones"},
        "boot_reinicios": {"estado": "PARCIAL", "detalle": "2 reinicios en 7d"},
        "autorizacion": {"estado": "OK", "detalle": "autorizaciones mayormente correctas"},
        "inicio_sesion": {"estado": "OK", "detalle": "inicio consistente"},
        "continuidad": {"estado": "PARCIAL", "detalle": "interrupciones aisladas"},
        "cierre_sesion": {"estado": "INCONSISTENTE", "detalle": "algunos cierres sin meterStop"},
    }

    r = validate_flow_ocpp_shape(flow)
    print("flow_ok", r.ok, "errors", r.errors)
    return 0 if r.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
