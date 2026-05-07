# Email Proactive Strict Filter v1

Objetivo: evitar notificaciones sin valor. Solo se notifica si hay contenido relevante accionable.

Reglas estrictas:
1) Prioridad P1 si `laia@grid-code.tech` está en TO.
2) Prioridad P2 si `laia@grid-code.tech` está en CC.
3) Excluir ruido (newsletters/social/promociones).
4) Exigir señal mínima de novedad: `unread` o `updated_recently`.
5) Si no hay relevantes: resultado vacío (`NO_NOTIFY`).

Módulo:
- `shared/orchestration/email_proactive_strict_filter_v1.py`
