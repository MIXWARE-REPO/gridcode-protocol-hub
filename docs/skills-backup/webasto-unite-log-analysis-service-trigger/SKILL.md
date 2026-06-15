---
name: webasto-unite-log-analysis-service-trigger
description: "Trigger operativo para análisis rígido de logs Webasto Unite: identifica cargador, descarga logs, genera JSON/HTML/PDF canónicos y envía por IMAP/SMTP si aplica."
version: 1.0.0
author: Hermes
tags:
  - webasto
  - unite
  - logs
  - analysis
  - pdf
  - html
  - trigger
  - imap
---

# Webasto Unite Log Analysis Service Trigger

Skill operativa para ejecutar, sin discusión adicional, el servicio completo de análisis de logs de un cargador Webasto Unite.

La única parte variable es el dictamen técnico derivado del log. Todo lo demás es contractual, determinista y repetible.

## Triggers de activación
Activar esta skill cuando el usuario pida cualquiera de estas variantes:
- "analiza el cargador"
- "analiza los logs"
- "haz un análisis de eventos OCPP"
- "sácame un informe del cargador"
- "revisa el Webasto Unite de la plaza X"
- cualquier solicitud equivalente sobre un Webasto Unite con intención de informe final

## Fuentes de verdad
- Runbook canónico: `docs/webasto_unite_log_runbook_v1.md`
- Schema contractual: `references/webasto-unite-log-analysis.schema.json`
- HTML canónico aprobado por el usuario
- JSON contractual del contrato Webasto Unite
- Flujo de adquisición separado: `webasto-unite-playwright-protocol-split`

## Archivos de apoyo
- `references/runbook-operativo.md`
- `references/checklist-preflight.md`
- `references/checklist-postrun.md`
- `references/input-contract.example.json`
- `references/example-operational.json`
- `references/example-degraded.json`
- `references/example-critical.json`

## Orden obligatorio de ejecución
1. Identificar el cargador.
2. Clasificar red.
3. Descargar logs.
4. Ejecutar preflight.
5. Generar JSON de análisis.
6. Renderizar HTML canónico.
7. Convertir a PDF.
8. Guardar localmente.
9. Ejecutar postrun validation.
10. Enviar mail solo si aplica, por IMAP/SMTP directo.

## Reglas de identificación
- Si el usuario da un solo dato, consultar Supabase para resolver el cargador exacto.
- Si el usuario da dos datos consistentes, procesar directo.
- Si hay ambigüedad, bloquear y pedir el dato mínimo faltante.
- No asumir identidad por memoria.
- No inventar plaza, edificio, site ni IP.

## Reglas de red
- Si la IP resuelta comienza por `192.`, se trata de laboratorio.
- En ese caso, usar el protocolo Playwright del cargador para descargar logs OCPP/HMI.
- La conexión y descarga de logs son un rail previo, separado del análisis.

## Skills encadenadas
1. `webasto-unite-playwright-protocol-split`
2. `production-preflight-check`
3. `webasto-unite-log-analysis-production-report`
4. `production-postrun-validator`
5. `email-style-grid-code` + rail IMAP/SMTP directo, solo si aplica

## Contrato de salida
Siempre producir:
- JSON de análisis validado
- HTML canónico
- PDF final
- guardado local
- evidencia trazable
- postrun OK

Si aplica mail:
- correo enviado por IMAP/SMTP directo
- asunto y cuerpo coherentes con el caso

## Reglas del informe
- El HTML no interpreta logs: solo pinta variables ya resueltas.
- El PDF debe derivar del mismo HTML fuente.
- El título del cuerpo debe usar la fuente del cuerpo, no la de la marca.
- El semáforo y la barra de valoración deben seguir la lógica contractual.
- El timeline debe tener exactamente 7 días.
- No usar texto exploratorio ni recomendaciones de visita sin acción útil.

## Mail
- El correo se gestiona por IMAP/SMTP directo.
- No usar Gmail UI.
- Antes de enviar, aplicar el estilo de `email-style-grid-code`.

## Regla de oro
No se debate el HTML, el PDF ni la estructura del flujo en cada ejecución.
Se reutiliza la base canónica y solo cambia la evaluación técnica del log.
