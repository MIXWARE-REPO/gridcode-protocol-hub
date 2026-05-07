# email_interpret_v1

Microprotocolo stage `interpret` del canal email.

## Regla de negocio activa (2 niveles de importancia)

Todo mail entrante se trata como ticket, pero con dos niveles:

- P1 (`priority = p1`): Laia está en `to` (destinataria directa).
  - `requires_reply = true`
  - `action = reply_required`
  - Mensaje de coordinación a Dario (`p1_assist_message`):
    "Me llegó un mail de {remitente} con un requerimiento por {tópico}; está esperando respuesta. ¿Qué enfoque le damos?"

- P2 (`priority = p2`): Laia está en `cc` o no está en `to`.
  - `requires_reply = false`
  - `action = notify_dario_watch` (si está en cc) o `watch`
  - Aviso corto (`p2_notification`) de 1 línea:
    "Nos llegó un mail por {tópico}; cualquier cosa nos dice."

Caso especial:
- Reenvío (`is_forward = true`) en P2 -> `action = watch_forward`.

## Señal técnica adicional

`technical_urgency = true` cuando el texto contiene señales de incidencia (ej. "no carga", "caído", "ticket", "gc-ev-").

Esta señal no rompe la regla de P1/P2; sirve para priorizar internamente dentro del mismo nivel.

## Nota de ejecución de respuesta P1

Cuando Dario define el enfoque (ej. "decirle semana próxima"), la respuesta al cliente se arma en el hilo con estilo formal y contextual: inicio con "Buenas", agradecimiento, propuesta concreta y cierre cordial.