# Webasto/Unite Input Contract

Este documento define el input oficial que debe recibir cualquier agente o runner para actuar sobre un cargador Webasto/Unite.

## Objetivo
Evitar ambigüedad, obligar a identificar primero el cargador y dejar explícito:
- qué acción se quiere ejecutar,
- sobre qué cargador,
- cómo se conecta a él,
- qué evidencia se espera,
- y qué fuente de verdad se usó.

## Fuente canónica de identidad
Antes de ejecutar cualquier acción, el cargador debe resolverse en:
- `website/docs/reference/supabase-charger-registry-schema.sql`

## Regla de identificación
- 1 dato disponible: verificar ese dato.
- 2 datos disponibles: confrontarlos.
- Si no hay identificación unívoca: no ejecutar.

## Clasificación de red
| IP | Red | Conexión | Skill / camino |
|---|---|---|---|
| `10.x.x.x` | COLONIAL | Indirecta vía VPN | `colonial-vpn-charger-access` |
| `192.168.31.x` | Laboratorio | Directa en LAN | runner Playwright directo |

## Campos oficiales del input
Campos obligatorios:
- `run_id`
- `action`
- `charger_ip`

Campos recomendados para individualización:
- `plaza`
- `serie`
- `id_colonial`
- `charger_label`

Campos operativos:
- `username`
- `password`
- `ocpp_endpoint`
- `free_charge_mode_active`
- `download_logs`
- `download_wait_seconds`
- `set_static_network`
- `static_ip`
- `netmask`
- `gateway`
- `dns_primary`
- `do_soft_reset`
- `do_hard_reset`
- `headless`

## Acciones válidas
- `change_id`
- `change_ocpp_endpoint`
- `download_event_log`
- `firmware_update`

## Reglas por acción
### 1) change_id
- Requiere individualización previa.
- Debe producir evidencia de persistencia.

### 2) change_ocpp_endpoint
- Requiere verificación previa en OCPP Settings.
- Debe guardar, reingresar y comparar antes/después.

### 3) download_event_log
- Requiere acceso a System / System Maintenance.
- Debe devolver evidencia de descarga real.

### 4) firmware_update
- Fuera del happy path hasta existir runner dedicado.

## Salida esperada
La ejecución debe devolver:
- cargador identificado,
- red clasificada,
- vía de conexión elegida,
- runner seleccionado,
- prechecks,
- evidencia,
- bloqueos si faltan datos.

## Fuentes de verdad enlazadas
- Runbook: `docs/runbook-colonial-ocpp-webasto-unite-v1.md`
- Checklist: `docs/webasto-unite-agent-checklist.md`
- Control contract: `docs/webasto-unite-control-contract.md`
- VPN skill: `productivity/colonial-vpn-charger-access/SKILL.md`
- Supabase schema: `website/docs/reference/supabase-charger-registry-schema.sql`
