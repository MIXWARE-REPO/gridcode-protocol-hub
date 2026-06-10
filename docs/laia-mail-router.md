# Laia Mail Router

Router ejecutivo para correo por IMAP dentro de Hermes Agent.

## Objetivo
Centralizar la decisión sobre el correo entrante para evitar duplicidad entre skills parecidas.

## Skills absorbidas
- gridcode-email-rail-hybrid
- gridcode-proactive-email-strict-review
- gridcode-mail-rail-autonomous

## Qué hace
- clasifica intención
- detecta si el hilo es interno, externo o híbrido
- prioriza P1/P2/P3
- evalúa riesgo
- decide silencio, draft, ejecución o aprobación
- enruta a subskills o protocolos concretos
- expone un catálogo verificado de capacidades internas con triggers por mailto para reutilización inmediata

## Catálogo interno verificado
Cuando el destinatario es equipo interno, la respuesta puede incluir un bloque de capacidades con enlaces tipo `mailto:`. Cada línea arranca con `>` para que el equipo la vea como opción accionable.

Capacidades verificadas:
1. Hacer una meet
2. Consignar una tarea o evento en calendario
3. Buscar algun archivo en Drive
4. Hacer informes o reportes comerciales tecnicos o administrativos
5. Hacer reportes para cargadores que se han de visitar on-site
6. Hacer informes remotos sobre los logs de eventos de los cargadores
7. Hacer certificados de validacion OCPP

## Reglas base
- Si no hay novedad real: `[SILENT]`
- Dominio autorizado no implica permiso absoluto
- Hilos híbridos suben el nivel de cautela
- Acciones sensibles requieren aprobación
- Acciones críticas se bloquean o escalan

## Subskills de salida
- mail-triage
- mail-reply-operational
- calendar-meet-host-gridcode
- gridcode-drive-api-first-governance
- gridcode-preliminary-analysis-report
- certificate-generation
- mail-contact-update
