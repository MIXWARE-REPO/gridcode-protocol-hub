# Webasto/Unite Strict Playwright Protocol v1

Objetivo: ejecutar un flujo reproducible para gestión de cargadores Webasto/Unite con contrato de entrada/salida y evidencia auditable.

## Script
- `scripts/webasto_unite_strict_playwright.py`

## Entrada
- Archivo JSON (`--input`) con:
  - identificación del cargador
  - credenciales
  - endpoint OCPP
  - política `free_charge_mode_active`
  - política de descarga de logs
  - flags de reset

Ejemplo:
- `examples/webasto_unite_strict_input.json`

## Ejecución
`python3 scripts/webasto_unite_strict_playwright.py --input examples/webasto_unite_strict_input.json --output out/webasto_unite_result.json`

## Salida
JSON contractual (`--output`) con:
- `status` (`ok|error`)
- `applied` (qué política se pidió aplicar)
- `result.actions|warnings|errors`
- `result.ocpp_before|ocpp_after`
- `artifacts` (carpeta run, capturas, descargas, json crudo)

## Reglas operativas incluidas
1. OCPP endpoint modificable por input.
2. `Free Charge Mode Active` controlado por input (recomendación estándar backend: `false`).
3. Descarga de logs habilitable con timeout amplio (normal latencia 20s-3min+).
4. Hard reset solo si se solicita explícitamente.

## Nota
La configuración de red está modelada en input para contrato, pero la automatización actual prioriza OCPP + logs + hard reset. Si se requiere aplicar Network Interfaces y Soft Reset en UI, se extiende el módulo `shared/orchestration/charger_webui_playwright_v1.py` con esos selectores/acciones del modelo exacto.
