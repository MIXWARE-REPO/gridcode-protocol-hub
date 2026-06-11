# Webasto/Unite Control Contract

Este documento define el contrato operativo mínimo para que un agente sepa:
- cómo identificar el cargador,
- cómo decidir si la conexión es directa o por VPN,
- qué runner usar según la acción,
- qué esperar antes, durante y después,
- y qué rutas/documentos son fuente de verdad.

## Fuente canónica de identidad del cargador
La identidad del cargador siempre se resuelve primero en:

- `website/docs/reference/supabase-charger-registry-schema.sql`

Regla base:
- 1 dato disponible: verificar ese dato.
- 2 datos disponibles: confrontarlos.
- Si la identificación no es unívoca, no ejecutar acción.

## Clasificación de red
| IP / dato | Red | Conexión | Skill / camino |
|---|---|---|---|
| `10.x.x.x` | COLONIAL | Indirecta vía VPN | `colonial-vpn-charger-access` → conectar a VPN → luego runner Playwright |
| `192.168.31.x` | Laboratorio | Directa en LAN | runner Playwright directo |
| 1 dato | — | Verificar ese dato | Continuar solo si identifica unívocamente |
| 2 datos | — | Confrontar ambos | Deben coincidir antes de actuar |

## Skill de conexión a COLONIAL
- Nombre: `colonial-vpn-charger-access`
- Ruta: `productivity/colonial-vpn-charger-access/SKILL.md`
- Propósito: conexión operativa a VPN Colonial (Saiwall/OpenVPN + MFA) y validación de acceso web a cargadores por IP interna.

## Camino obligatorio
1. Identificar el cargador en Supabase.
2. Clasificar la red por IP.
3. Resolver la vía de conexión:
   - directo si es laboratorio,
   - VPN si es COLONIAL.
4. Elegir runner específico de la acción.
5. Ejecutar la acción y validar persistencia/evidencia.

## Mapa de acciones
### A. Cambio de ID
- Objetivo: ajustar el ID del cargador.
- Estado: camino soportado por Playwright/script.
- Expectativa: guardar, reentrar y confirmar persistencia.
- Evidencia mínima: HTML antes/después y screenshot final.

### B. Cambio de endpoint OCPP
- Objetivo: modificar `Central System Address`.
- Runner base actual: `scripts/webasto_unite_strict_playwright.py`
- Regla: guardar + salir + reingresar + verificar persistencia.
- Expectativa: el endpoint post-run debe coincidir con el objetivo.

### C. Descarga de log de eventos
- Objetivo: obtener el ZIP de logs/eventos.
- Runner base actual: `scripts/webasto_unite_strict_playwright.py`
- Nota: la descarga puede tardar; no marcar fallo prematuro si el navegador queda esperando mientras el ZIP se genera.
- Expectativa: archivo ZIP en la carpeta de evidencias.

### D. Actualización de firmware
- Objetivo: actualizar firmware.
- Estado: fuera del happy path hasta existir runner dedicado y validado.
- Regla: no improvisar con los runners de ID/OCPP/logs.

## Paths útiles
- Runbook operativo: `docs/runbook-colonial-ocpp-webasto-unite-v1.md`
- Contrato de control: `docs/webasto-unite-control-contract.md`
- Skill VPN COLONIAL: `productivity/colonial-vpn-charger-access/SKILL.md`
- Schema Supabase de cargadores: `website/docs/reference/supabase-charger-registry-schema.sql`
- Runner strict Webasto: `scripts/webasto_unite_strict_playwright.py`
- Runner unificado CPMS/WebUI: `scripts/webasto_unite_cpms_unified_playwright_v2.py`

## Qué debe esperar el agente
- Antes de tocar UI: identidad resuelta.
- Antes de conectar: red clasificada.
- Antes de afirmar éxito: persistencia verificada.
- Si algo no coincide: bloquear y pedir el dato mínimo faltante.
- Snapshots: solo fallback documentado.

## Formato de salida recomendado
El agente debe responder con:
- cargador identificado,
- red clasificada,
- vía de conexión elegida,
- runner seleccionado,
- resultado esperado,
- evidencia generada,
- bloqueos si faltan datos.
