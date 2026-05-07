# Protocolo Infranqueable v1 — Interpretación OCPP + Reporte HTML consistente

Objetivo: producir un HTML técnico coherente con la realidad del cargador en cada ejecución, sin texto heredado ni incoherencias.

## 1) Entrada canónica obligatoria
- `metadata`:
  - `charger_id`, `client`, `location`, `ticket_id`, `analyst`, `issued_at`, `window_start`, `window_end`
  - opcionales: `ip`, `serial_number`, `firmware`, `ocpp_version`
- `events[]`:
  - `timestamp` (ISO)
  - `message_type` (Authorize, StartTransaction, StopTransaction, MeterValues, Heartbeat, BootNotification, StatusNotification, TransactionEvent, etc.)
  - `payload` (dict)

## 2) Reglas de interpretación (infranqueables)
1. Solo ventana de 7 días (`window_start`..`window_end`).
2. Sesión válida si existe inicio + cierre coherente.
3. Intento incompleto = observación (no falla estructural) salvo recurrencia.
4. La evaluación final depende de evidencia agregada:
   - BIEN: efectividad >= 80 y sin patrón recurrente de incompletos.
   - REGULAR: efectividad 50..79 o incompletos recurrentes sin caída estructural.
   - REQUIERE INTERVENCIÓN: efectividad < 50 o fallas recurrentes de conectividad/cierre/autorización.
5. Nunca usar texto hardcodeado heredado de otro cargador.

## 3) Salida canónica
`report_context` con:
- cabecera de cargador y metadatos
- resumen de salud (`efectividad`, `banda`, `evaluacion_final`)
- actividad por día (7 filas)
- flujo OCPP por etapas
- métricas agregadas
- detalle_eventos
- interpretación técnica
- diagnóstico y acción

## 4) Render HTML determinista
- El renderer solo consume `report_context`.
- Si un dato no existe: `N/D en log`.
- No se agregan campos fuera del template.
- No se permite mezclar eventos de otros casos.

## 5) Validaciones previas al render
- 7 días exactos en timeline.
- `charger_id` del header coincide con `report_context.charger_id`.
- `analyst` consistente con metadata.
- Eventos destacados no vacíos cuando hay actividad.
- Evaluación final coherente con métricas.

## 6) Resultado
- HTML consistente con realidad del cargador.
- Si estado es BIEN/REGULAR/REQUIERE INTERVENCIÓN, toda la narrativa y diagnóstico deben reflejar exactamente ese estado.
