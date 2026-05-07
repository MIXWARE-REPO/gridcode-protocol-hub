# Política de salida de emails — timing, recuperación y corrección

## 1) Horarios y días laborales

Regla:
- Si el envío cae fuera de horario laboral, se retiene y se posdata.
- Franja laboral: lunes a viernes, 09:00 a 18:00 (Europa Central).
- Si cae viernes noche o fin de semana, se programa al próximo lunes 09:00.

Sugerencia obligatoria al usuario (fuera de horario):
- Mostrar (tono colega): "Te parece que lo enviemos mañana mejor?" (o "...el lunes..." según corresponda).
- Confirmación directa:
  - negativa: "No, envialo ahora"
  - afirmativa: "Sí, tienes razón, envialo luego"

Excepción:
- Se permite forzar envío fuera de horario solo cuando se indique explícitamente.

## 2) Recuperación de emails enviados

Regla operativa:
- No se asume recuperación real tras entrega SMTP.
- Si un email sale mal, se aplica protocolo de fe de erratas por reply-all.

Pasos:
1. Detectar error.
2. Frenar nuevos envíos del mismo hilo hasta corregir.
3. Enviar fe de erratas con disculpa breve + contenido corregido.
4. Mantener reglas de copia (Dario + extras por categoría).

## 3) Reglas de envío

Siempre:
- Copiar a `dario@grid-code.tech`.
- Responder con `reply-all`.
- Nunca respuesta individual aislada.

Además por categoría:
- Administrativo: copiar también a `lorena@grid-code.tech`.
- Soporte: copiar también a `support@grid-code.tech`.

## 4) Reenvíos internos de @grid-code.tech

Cuando un miembro interno reenvía un hilo para que Laia tome seguimiento:
- Analizar hilo completo e interactuantes.
- Responder al hilo original (sin prefijo FW/Fwd en asunto).
- Presentarse al entrar en conversación.

Plantilla de entrada:
"Buenas, soy Laia. [Nombre interno] me pidió que diera seguimiento a este tema y se le dará prioridad para avanzar de forma ordenada."

## Implementación Python

- `shared/orchestration/email_delivery_policy_v1.py`
  - `decide_delivery_time()`
  - `build_recipients()`
  - `normalize_subject_for_reply()`
  - `build_internal_forward_intro()`
  - `build_errata_message()`
  - `build_recovery_protocol_note()`
