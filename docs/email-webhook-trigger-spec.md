# Email Webhook Trigger Spec (v1)

Objetivo: reemplazar canal no fiable por un trigger webhook explícito y deduplicado para iniciar el rail de gestión.

## Trigger principal

Endpoint webhook recibe eventos de correo en tiempo real.

Evento mínimo requerido:
- provider
- account
- event_type: new_message | thread_update | message_updated
- message_id
- thread_id
- event_ts

## Seguridad

- Firma HMAC SHA256 en header (ej: `X-Event-Signature`).
- Verificación con secreto compartido.
- Si falla firma => rechazo.

## Dedupe

- `dedupe_key = sha256(provider|account|message_id|thread_id|event_ts)`
- Si `dedupe_key` ya existe, rechazar como duplicado.

## Acción al aceptar

1) Construir evento canónico inbound.
2) Disparar pipeline de email (`pipeline_email_v1`).
3) Registrar aceptación en log operativo.

## Fallback recomendado

- Polling de respaldo cada 15 min en horario laboral CET/CEST para detectar huecos de webhook.
- Si aparece mail no visto en webhook, se inyecta evento sintético con `event_type=message_updated`.

## Implementación Python

- `shared/orchestration/email_webhook_trigger_v1.py`
  - `verify_signature(raw_body, signature, secret)`
  - `evaluate_trigger(payload, seen_keys)`
  - `build_inbound_update_event(payload)`

## Resultado

Con esto, el trigger del rail pasa a ser un webhook confiable y verificable, no notificaciones ocasionales.