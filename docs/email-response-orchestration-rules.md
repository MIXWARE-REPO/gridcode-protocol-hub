# Reglas principales — Orquestación de respuestas por email

Objetivo: cuando Dario indique una frase breve para responder un email, el sistema debe:
1) contextualizar con el hilo,
2) aplicar estilo Grid Code,
3) preparar confirmación de la respuesta,
4) y crear seguimiento proactivo si hay compromisos de tiempo.

## Reglas núcleo

1. Entrada por necesidad de negocio
- Dario puede indicar frases como:
  - "contestale que lo recibimos y lo vemos mañana"
  - "contestale que eso no va, lo dice en mi mail anterior"
  - "contestale lo que sea"

2. Contexto obligatorio
- Recuperar contexto del hilo, remitente y tema activo antes de redactar.

3. Estilo obligatorio
- Aplicar guía `email-style-grid-code`.
- Inicio con "Buenas".
- Sin tuteo al cliente.
- Sin prometer inmediatez.
- Firma exacta:
  Saludos,
  Laia

4. Confirmación proactiva
- Antes/de inmediato al envío, generar bloque de confirmación con:
  - destinatario,
  - asunto,
  - body final,
  - compromisos detectados,
  - tareas proactivas a programar.

5. Compromisos => actividad real en Google Tasks
- Si el texto compromete "mañana" o "semana próxima", crear tarea de seguimiento.
- La tarea se crea asignada a `dario@grid-code.tech`.
- Siempre consultar franja con doble opción:
  - `manana`
  - `tarde`
- Con la franja elegida, se genera payload para crear la tarea en Google Tasks.

## Implementación

Módulo Python:
- `shared/orchestration/email_response_orchestrator_v1.py`

Función principal:
- `orchestrate_email_response(payload)`

Salida estructurada:
- `style_validation`
- `confirmation`
  - `commitments`
  - `proactive_tasks`
- `task_creation`
  - provider: google_tasks
  - needs_user_slot_confirmation
  - slot_options
  - payloads

## Resultado operativo esperado

No solo se responde el email: también se garantiza orden y ejecución de compromisos asumidos mediante tareas reales.