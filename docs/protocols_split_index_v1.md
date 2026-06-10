# Protocolos separados (arquitectura por objetos)

1) Protocolo WebUI Webasto/Unite
- Script: `scripts/webasto_unite_strict_playwright.py`
- Orquestador OOP: `shared/orchestration/charger_webui_playwright_v1.py`
- Input ejemplo: `examples/webasto_unite_strict_input.json`

2) Protocolo CPMS
- Script: `scripts/run_cpms_playwright_v1.py`
- Orquestador OOP: `shared/orchestration/cpms_playwright_v1.py`
- Input ejemplo: `examples/cpms_playwright_input_v1.json`

3) Protocolo NUBA Monitoring (base operativa, pendiente selectors Playwright)
- Script: `scripts/run_nuba_monitoring_protocol_v1.py`
- Doc funcional: `docs/nuba-monitoring-protocol-v1.md`
- Input ejemplo: `examples/nubas_monitoring_input_v1.json`

4) Protocolo Laia Mail Router
- Script: `scripts/run_laia_mail_router.py`
- Orquestador: `shared/orchestration/laia_mail_router_v1.py`
- Input ejemplo: `protocols/email/router/schema.input.json`

## Nota
Se operan de forma independiente para evitar arrastre de fallos entre dominios.
