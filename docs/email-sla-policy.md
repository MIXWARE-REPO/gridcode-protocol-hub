# Política SLA — Email (P1/P2)

Política activa confirmada con Dario.

## Reglas

- P1 (`priority = p1`)
  - `sin_respuesta`: alerta a 24 horas.
  - `pidio_ajuste`: atención prioritaria en el día.

- P2 (`priority = p2`)
  - `sin_respuesta`: alerta a 48 horas.
  - `pidio_ajuste`: atención prioritaria en el día.

## Implementación técnica

La política vive en:
- `shared/learning/email_sla_policy_v1.py`

API:
- `get_sla(priority)` -> devuelve configuración SLA por prioridad.
