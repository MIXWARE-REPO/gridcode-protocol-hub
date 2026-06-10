# Charger WebUI E2E v1 (Python + Playwright + JSON + HTML + PDF)

## Objetivo
Ejecución consistente con un único comando:
- Login en WebUI del cargador
- Gestión OCPP (endpoint + variables)
- Descarga de logs OCPP
- Reinicio opcional
- Análisis técnico en JSON
- Render HTML de análisis agregado
- Conversión a PDF

## Script principal
`scripts/run_charger_e2e_playwright.py`

## Entradas mínimas
- `--ip`
- `--password`
- `--ticket-id`

Opcionales:
- `--username admin`
- `--endpoint ws://...`
- `--ocpp-var name=value` (repetible)
- `--reboot --allow-unsafe-actions`

## Comando ejemplo
```bash
cd /home/laia/gridcode-protocol-hub
source .venv/bin/activate
python3 scripts/run_charger_e2e_playwright.py \
  --ip 192.168.31.138 \
  --password 'TU_PASSWORD' \
  --ticket-id GC-EV-TEST-20260508-0001 \
  --endpoint ws://192.168.31.165/ws/ocpp \
  --ocpp-var selectOCPPConnection=1
```

## Salidas
En:
`out/playwright_e2e/<ticket>_<ip>/`

Archivos:
- `00_run_summary.json`
- `01_webui_output.json`
- `02_analysis_output.json`
- `03_report_filled.html`
- `04_report.pdf`
- `evidence/` (capturas + htmls + logs zip descargados)

## Guardrails
- `reboot` bloqueado si no se pasa `--allow-unsafe-actions`.
- No se asume persistencia de cambios OCPP sin relectura.
- Si no hay eventos parseables en ZIP, se genera contexto mínimo para no romper el pipeline y se marca por evidencia.

## Dependencias
- `playwright` en `requirements.txt`
- Ejecutar una vez:
```bash
playwright install chromium
```
- Para PDF: `google-chrome` disponible en host.
