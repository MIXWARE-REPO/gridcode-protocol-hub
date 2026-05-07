# Guía oficial — Form-RemoteS (Interpretación de logs OCPP 7 días)

Fuente: especificación validada (Dario) recibida el 2026-05-07.

## Propósito
Analizar logs OCPP de un cargador individual en ventana de 7 días y producir JSON estructurado para rellenar el informe remoto agregado.

## Entradas mínimas
- Metadatos:
  - charger_id, cliente, ubicación, ticket_id, analista, fecha_emision, ventana_inicio, ventana_fin
- Eventos OCPP por cargador:
  - timestamp
  - tipo_mensaje (BootNotification, StatusNotification, Authorize, StartTransaction, StopTransaction, MeterValues, Heartbeat, TransactionEvent, etc.)
  - direction (si existe)
  - payload_relevante (idTag, transactionId, meterStart/meterStop, status, errorCode, reason)

## Protocolo de análisis (resumen operativo)

1) Filtrado y agrupación:
- Filtrar a ventana_inicio 00:00 -> ventana_fin 23:59.
- Agrupar por día calendario.
- Detectar sesiones (Start/Stop o TransactionEvent Start/End).
- Marcar sesiones completas vs anómalas.

2) Actividad por día (categorías):
- Carga registrada
- Carga con anomalía
- Sin carga registrada
- Sin evidencia suficiente

3) Flujo operativo OCPP por etapas:
- acceso_remoto
- backend
- boot_reinicios
- autorización
- inicio_sesion
- continuidad
- cierre_sesion
Cada etapa con estado: OK | PARCIAL | INCONSISTENTE | SIN_EVIDENCIA + detalle.

4) Métricas agregadas 7 días:
- sesiones_totales
- sesiones_exitosas
- cargas_fallidas_referidas
- interrupciones_sesion
- reinicios_detectados
- dias_con_actividad
- dias_sin_actividad
- desconexiones_backend
- boot_por_dia
- cierres_automaticos
- rechazos_auth
- sin_cierre_consistente
- efectividad = sesiones_exitosas / sesiones_totales * 100

Bandas de salud por efectividad:
- >70: SANO
- 50-70: SEGUIMIENTO ACTIVO
- 40-50: ATENCIÓN ALTA
- <40: PRIORIDAD MÁXIMA

5) Detalle de eventos destacados:
- BootNotification relevantes
- Cierres inconsistentes
- Status críticos (SuspendedEV/SuspendedEVSE/Faulted)
- Errores repetitivos

6) Interpretación técnica:
- Resumir autorización, backend, inicio/continuidad/cierre y rol de reinicios.
- Identificar patrón dominante de degradación.

7) Diagnóstico y siguiente paso:
- hallazgo_dominante
- causa_probable
- accion_recomendada
- condicion_escalado

## Salida esperada
JSON estructurado para el Form-RemoteS con bloques:
- cabecera
- resumen_salud
- actividad_por_dia[]
- flujo_ocpp{}
- metricas{}
- detalle_eventos[]
- interpretacion_tecnica
- diagnostico{}
- evidencia{}

## Estilo
- es-ES neutro
- técnico, claro, conciso
- decisión técnica verificable
