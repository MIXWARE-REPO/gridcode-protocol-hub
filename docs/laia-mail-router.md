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
