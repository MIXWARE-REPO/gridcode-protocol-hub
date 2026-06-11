# FASE 1.5 — Telegram Behavior + Email Behavior en 11 skills

## Objetivo
Añadir a 11 skills seleccionadas dos secciones estándar cuando falten:
1. `## Telegram Behavior`
2. `## Email Behavior`

Después, revalidar que cada skill cumpla el set mínimo estructural de 9 secciones.

## Scope
Excluir explícitamente:
- `linkedin-li-preset-v1`

Skills a corregir:
1. `ticket-handler`
2. `calendar-meet-host-gridcode`
3. `onsite-mobile-pdf-form-design`
4. `webasto-unite-log-analysis-production-report`
5. `webasto-full-production-run`
6. `nuba-full-production-run`
7. `mindcode-create-discussion`
8. `github-repo-management`
9. `webasto-set-ocpp-endpoint`
10. `gridcodear-documentos`
11. `gestion-de-mails-laia`

## Criterio de orden de trabajo
Voy de mayor impacto operativo a menor, priorizando:
1. skills de correo y soporte
2. skills de agenda/meet y docs
3. skills de operación Webasto/NUBA
4. skills de integración general (GitHub / MindCode)

## Orden de ejecución propuesto

### 1) `ticket-handler`
Cambios exactos:
- Añadir `## Telegram Behavior` si no existe.
- Añadir `## Email Behavior` si no existe.
- Normalizar el flujo de activación por Telegram:
  - qué dato mínimo pedir si falta el ticket_id (`GC-EV-*` o cache reciente)
  - cómo responder breve en Telegram
  - cómo resolver ambigüedad de “ese ticket”
- Normalizar el flujo de email:
  - confirmar ID del ticket y estado actual antes de responder/cerrar
  - aclarar que todo email debe seguir el manual de estilo
  - definir qué se hace si falta contexto o el body no cumple
- Verificar que queden visibles las secciones mínimas y que `Layout`/`Cómo responder`/`Cómo cerrar` no queden como únicos bloques de procedimiento.

### 2) `gestion-de-mails-laia`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - qué pedir cuando llega un prompt ambiguo sobre un hilo
  - cómo responder corto y operacional
  - cómo manejar referencias anafóricas a “ese mail”
- Email:
  - cómo parsear hilo completo
  - qué confirmar antes de redactar o responder
  - cómo resolver hilos internos/externos/mixtos
- Alinear con el manual `email-style-grid-code` sin duplicar reglas incompatibles.

### 3) `calendar-meet-host-gridcode`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir fecha, hora, zona horaria, participantes y tipo de acción (Meet vs recordatorio)
  - responder breve con confirmación de datos faltantes
- Email:
  - confirmar participantes, asunto, objetivo y si debe haber RSVP
  - aclarar si la respuesta debe salir en hilo o como mail nuevo
- Mantener el contrato I/O y los caminos canónicos ya existentes.

### 4) `gridcodear-documentos`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir tipo documental, público objetivo y formato final
  - resolver ambigüedad entre técnico / administrativo / comercial
- Email:
  - confirmar finalidad del documento, destinatario y tono
  - pedir datos mínimos para construir el PDF sin bloquear el flujo
- No tocar el canon visual ni la nomenclatura A/T/C salvo para referenciarlo mejor.

### 5) `onsite-mobile-pdf-form-design`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir contexto de campo, modelo de formulario y número de páginas
  - responder corto si faltan datos del onsite
- Email:
  - confirmar si el PDF será para imprimir o completar en móvil
  - aclarar campos obligatorios y restricciones de compatibilidad
- Mantenerlo como skill especializada, sin mezclarlo con el documento corporativo general.

### 6) `webasto-unite-log-analysis-production-report`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir plaza, edificio, ticket, periodo de logs y audiencia
  - responder breve con lo que falta para arrancar análisis
- Email:
  - confirmar el ticket/caso, alcance y si el cliente o mantenedor es el destinatario
  - pedir archivo/URL de análisis si no está incluido
- Refuerzo: dejar claro cuándo se produce informe y cuándo solo diagnóstico.

### 7) `webasto-full-production-run`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir IP/IP interna, objetivo del run, credenciales si aplican y flags de ejecución
  - responder con ambigüedad resuelta solo a nivel de seguridad/operación
- Email:
  - confirmar objetivo del run y qué parte del stack se va a tocar
  - pedir aprobación explícita si el cambio puede afectar persistencia o conectividad
- Alinear el workflow con preflight/runner/postrun.

### 8) `nuba-full-production-run`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir entorno, objetivo administrativo y credenciales/contexto si falta
  - responder corto con siguiente paso o dato faltante
- Email:
  - confirmar acción administrativa exacta
  - dejar explícito qué se validará al final
- Mantenerlo como runner backend, no como skill de análisis.

### 9) `webasto-set-ocpp-endpoint`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir IP, endpoint OCPP, entorno y confirma si hay que persistir o solo probar
  - responder breve, sin asumir que el valor ya está validado
- Email:
  - confirmar endpoint exacto, target charger y si hay ventana de cambio
  - pedir confirmación si se trata de una modificación potencialmente sensible
- Dejarlo explícitamente como helper/backend.

### 10) `mindcode-create-discussion`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir título, proyecto y objetivo de la discusión
  - responder breve con dudas de scope
- Email:
  - confirmar si la discusión es interna y qué contexto debe incluir
  - evitar confusión con tickets de soporte externos
- Mantener la separación estricta MindCode vs soporte por email.

### 11) `github-repo-management`
Cambios exactos:
- Añadir `## Telegram Behavior`.
- Añadir `## Email Behavior`.
- Telegram:
  - pedir repo, operación deseada y si hay remote/org/branch implicado
  - responder breve si falta auth o contexto de GitHub
- Email:
  - confirmar si la acción afecta repo, fork, release, workflow o secret
  - pedir repo URL exacta si no está presente
- Convertir el contenido pesado a referencias si conviene para progressive disclosure.

## Cambios transversales exactos en cada SKILL.md
Para cada uno de los 11:
- Insertar `## Telegram Behavior` con 4 puntos:
  - cómo se activa por Telegram
  - qué datos pedir
  - cómo responder breve
  - cómo manejar ambigüedad
- Insertar `## Email Behavior` con 4 puntos:
  - cómo parsear el email
  - qué confirmar antes de ejecutar
  - cómo responder
  - qué hacer ante falta de contexto
- Verificar que las 9 secciones mínimas queden presentes o, si ya existen con nombre distinto, dejar equivalencia explícita.

## Verificación final
Checklist por skill:
- SKILL.md existe
- frontmatter válido
- 9 secciones mínimas cubiertas
- Telegram Behavior presente
- Email Behavior presente
- progressive disclosure razonable

## Resultado esperado
- Los 11 skills quedan normalizados con comportamiento explícito por Telegram y por email.
- Se reduce ambigüedad operacional.
- La FASE 1 pasa de auditoría a hardening documental.
