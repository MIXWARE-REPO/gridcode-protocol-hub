# GridCode Protocol Hub — Paquete de Producción

Este paquete consolida los 3 procesos operativos con ejecución contractual (input/output JSON):

1. Webasto/Unite (cargador):
   - Runner: `scripts/webasto_unite_strict_playwright.py`
2. CPMS (EVA / PLUS / WINGS):
   - Runner: `scripts/cpms_wings_create_charger.py`
3. NUBA (cloud):
   - Runner: `scripts/run_nuba_playwright_v1.py`

## Estructura
- `production/templates/` -> JSON de entrada listos para copiar/editar
- `production/run/` -> scripts shell de ejecución por proceso
- `production/checklists/` -> validaciones pre/post ejecución

## Regla de operación
- Todo se ejecuta por JSON de entrada.
- Toda salida es JSON contractual.
- No se improvisan selectores en runtime (esquema irrompible).
