# Laia Mail Router

Router ejecutivo de correo para Hermes Agent.

## Función
- Clasificar mails por intención, prioridad, riesgo y tipo de hilo.
- Detectar dominio autorizado, remitente y contexto.
- Decidir silencio, notificación, draft, ejecución, aprobación o escalado.
- Enrutar a subskills o protocolos especializados sin duplicar lógica.

## Skills absorbidas
- gridcode-email-rail-hybrid
- gridcode-proactive-email-strict-review
- gridcode-mail-rail-autonomous

## Subskills de salida
- mail-triage
- mail-reply-operational
- calendar-meet-host-gridcode
- gridcode-drive-api-first-governance
- gridcode-preliminary-analysis-report
- certificate-generation
- mail-contact-update

## Regla base
Si no hay novedad real, el router devuelve `[SILENT]`.
