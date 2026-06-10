# Intent Routing -> Grupos de Producción

## Grupo 1: group-webasto-unite
Activar ante intenciones:
- enviar/conectar/apuntar un cargador
- analizar un cargador
- descargar log(s) de eventos de un cargador

Skills internas:
- webasto-full-production-run
- webasto-set-ocpp-endpoint
- webasto-verify-ocpp-persistence
- colonial-charger-analysis-execution
- ocpp-log-unpack-7d-analysis
- production-preflight-check
- production-postrun-validator

---

## Grupo 2: group-cpms-family
Activar ante intenciones:
- saber endpoint del CPMS
- crear/generar cargador en My Chargers
- crear usuario
- cambiar configuración en DLM

Skills internas:
- cpms-login-check
- cpms-full-production-run
- cpms-create-ac-single-phase-charger
- cpms-read-ocpp-endpoint
- production-preflight-check
- production-postrun-validator

---

## Grupo 3: group-nuba-cloud
Activar ante intenciones:
- control de instancias
- verificación por Teleport
- generación de códigos de activación
- gestión de licencias/activation codes

Skills internas:
- nuba-login-check
- nuba-full-production-run
- nuba-generate-activation-code-plus
- production-preflight-check
- production-postrun-validator

---

## Grupo 4: Laia Mail Router
Activar ante intenciones:
- correo operativo entrante
- triage proactivo
- órdenes por email
- autorización por dominio
- delay de acción por dominio interno/externo
- pedido de aprobación

Skills internas:
- laia-mail-router
- mail-triage
- mail-reply-operational
- calendar-meet-coordination
- drive-document-retrieval
- report-generation
- certificate-generation
- audit-trace
- access-control-policy

---

## Regla anti-mareo
Si una frase tiene sinónimos o alternativas, NO cambiar de grupo durante la misma tarea.
Seleccionar grupo por intención dominante y ejecutar dentro de ese grupo de forma determinista.