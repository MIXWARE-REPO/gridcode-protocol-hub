# Esquema irrompible v1 — Webasto/Unite + CPMS + NUBA

## Principio
No buscar selectores nuevos en cada corrida. Las 3 UIs se tratan como estáticas y se opera con selectores fijos versionados.

## Proceso 1: Webasto/Unite (cargador)
- Script: `scripts/webasto_unite_strict_playwright.py`
- Orquestador: `shared/orchestration/charger_webui_playwright_v1.py`
- Selectores fijos:
  - login: `input[name="username"]`, `input[name="pass"]`, `input#button_login[name="button_login"]`
  - menú OCPP: `a[href="index_ocpp.php"]`
  - endpoint: `input#centralSystemAddress[name="centralSystemAddress"]`
  - save: `input#ocpp_button[name="ocpp_button"]`
- Verificación obligatoria:
  1) guardar
  2) ir a Main
  3) volver a OCPP
  4) re-leer endpoint persistido

## Proceso 2: CPMS (EVA / PLUS / WINGS)
- Script: `scripts/cpms_wings_create_charger.py`
- Mismo backend para EVA/PLUS/WINGS: cambia URL + credenciales.
- Flujo estable:
  - login
  - MY CHARGERS
  - ADD CHARGER
  - alta
  - lectura OCPP URL en CONFIGURATIONS/CONNECTION SETTINGS

## Proceso 3: NUBA
- Script: `scripts/run_nuba_playwright_v1.py`
- Orquestador: `shared/orchestration/nuba_playwright_v1.py`
- Flujo estable:
  - login
  - Admin Zone
  - Activation Codes
  - botón + flotante
  - formulario + SAVE

## Contrato de salida
Todos deben devolver JSON con:
- status
- steps/actions
- warnings/errors
- evidencia mínima (html + screenshot)
- verificación de persistencia cuando aplique

## Regla operativa
Si una UI cambia, se versiona selector-map (v2) y no se “adivina” en runtime.