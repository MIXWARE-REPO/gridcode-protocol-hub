# Webasto/Unite + CPMS Unified Playwright v2

Script unificado que ejecuta en una sola corrida:
1) Fase cargador (WebUI):
- login
- set endpoint OCPP
- set Free Charge Mode Active
- descarga de logs
- hard reset opcional

2) Fase CPMS:
- login
- Chargers (alta opcional)
- Metrics (snapshot)
- Users (alta opcional)
- Settings (snapshot de secciones críticas)

## Script
`scripts/webasto_unite_cpms_unified_playwright_v2.py`

## Input ejemplo
`examples/webasto_unite_cpms_unified_input_v2.json`

## Ejecución
python3 scripts/webasto_unite_cpms_unified_playwright_v2.py \
  --input examples/webasto_unite_cpms_unified_input_v2.json \
  --output out/webasto_unite_cpms_unified_result_v2.json

## Output
JSON contractual con:
- status global
- resultado por fase (charger_phase, cpms_phase)
- acciones/warnings/errors
- snapshots críticos
- artifacts con rutas de evidencia

## Artefactos
Cada ejecución crea carpeta en:
`out/webasto-unite-cpms-unified/<timestamp>_<run_id>_<ip>/`
con:
- `charger_phase/01_charger_result.json`
- `cpms_phase/01_cpms_result.json`
- `00_unified_summary.json`
- capturas/html de evidencia
