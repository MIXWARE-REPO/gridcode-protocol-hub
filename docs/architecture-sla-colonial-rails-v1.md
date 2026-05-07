# Arquitectura Maestro v1 — SLA Colonial (Webasto UNITE)

Objetivo: estandarizar ejecución técnica y reportes con un rail híbrido estricto (Python + contratos), eliminando variaciones no controladas.

## Segmentación oficial

## Grupo 1 — Ticket de servicio (fuera de alcance)
- Responsable: flujo existente (Fran).
- Estado: estable, no se modifica.
- Función: proveer `ticket_id`, contexto cliente y cargador.

## Grupo 2 — Diagnóstico remoto agregado + operación remota
Incluye:
- análisis de logs OCPP (7 días),
- acceso remoto por Web UI/IP fija,
- configuración OCPP (endpoint ws:// y parámetros),
- reinicio/control remoto,
- decisión técnica de continuidad remota o escalado onsite.

Salida obligatoria:
- reporte remoto agregado con plantilla fija aprobada,
- misma estructura y campos en todas las ejecuciones,
- solo cambian datos dinámicos del caso.

## Grupo 3 — Ejecución onsite + reporte de visita
Se activa cuando:
- el Grupo 2 no puede ejecutarse, o
- el diagnóstico remoto escala por criticidad.

Incluye:
- visita técnica a campo,
- completado de PDF editable onsite,
- captura de evidencias fotográficas,
- identificación de receptor en sitio,
- consolidación final de reporte de visita.

## Principios de diseño
1) Contratos estrictos de entrada/salida (sin improvisación).
2) Separación entre lógica de negocio y adaptadores de infraestructura.
3) Invariancia visual de reportes aprobados.
4) Evidencia trazable por ticket+cargador.
5) Reglas SLA y criticidad como políticas explícitas.

## Arquitectura Python propuesta

- `rails/`
  - `group2_remote_rail.py`
  - `group3_onsite_rail.py`
  - `decision_bridge.py`  (decide remoto->onsite)

- `contracts/`
  - `ticket_input.py`
  - `remote_analysis.py`
  - `onsite_report.py`

- `adapters/`
  - `charger_ui_adapter.py`
  - `ocpp_log_adapter.py`
  - `pdf_template_adapter.py`
  - `evidence_adapter.py`

- `policies/`
  - `criticity_policy.py`
  - `escalation_policy.py`
  - `report_invariance_policy.py`

- `evidence/`
  - `artifact_registry.py`

## Flujo maestro
1) Entrada: ticket válido (Grupo 1).
2) Ejecutar Grupo 2 (remoto).
3) Clasificar criticidad y posibilidad de resolución remota.
4) Si no resuelve o no ejecutable => activar Grupo 3.
5) Emitir reporte remoto y/o onsite según aplique.
6) Registrar evidencias, hashes y estado final.

## Reglas de invariancia de reportes
- Prohibido rediseñar plantillas aprobadas.
- Prohibido alterar header/footer/frames.
- Prohibido overlays que dejen residuos/duplicados.
- Validación bloqueante antes de entrega:
  - no solapes,
  - no datos heredados,
  - campos obligatorios completos.

## Criterios de cierre de caso
- `resuelto_remoto`: sí/no
- `requiere_onsite`: sí/no
- `criticidad`: sano/seguimiento/alta/máxima
- `evidencia_completa`: sí/no
- `reporte_emitido`: remoto/onsite/ambos
