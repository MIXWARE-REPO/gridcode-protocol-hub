# Webasto Unite Log Analysis Runbook v1

## Objetivo
Estandarizar un flujo único, rígido e irrompible para analizar logs OCPP/HMI de cargadores Webasto Unite y producir siempre la misma clase de salida contractual para el cargador correspondiente.

La única variación permitida es la evaluación técnica del log.

## Cadena operativa canónica
1. Identificación del cargador.
2. Clasificación de red.
3. Descarga de logs.
4. Preflight rígido.
5. Generación de JSON de análisis.
6. Render HTML canónico.
7. Conversión a PDF.
8. Guardado local.
9. Postrun validation.
10. Envío por mail solo si aplica, vía IMAP/SMTP directo.

## Skills encadenadas
- webasto-unite-playwright-protocol-split
- production-preflight-check
- webasto-unite-log-analysis-production-report
- production-postrun-validator
- email-style-grid-code

## Reglas de adquisición
- Canal de entrada: Telegram o mail interno desde @grid-code.tech, @centual.eu, @fundacionnovacore.org.
- Si el usuario aporta un solo dato, consultar Supabase para resolver el cargador exacto.
- Si aporta dos datos consistentes, procesar directo.
- Si falta consistencia, bloquear y pedir el dato mínimo faltante.
- Si la IP resuelta empieza por 192.*, usar el protocolo Playwright de laboratorio para descargar logs OCPP/HMI.

## Script maestro propuesto
`scripts/run_webasto_unite_log_analysis_v1.py`

### Responsabilidad del script
- Orquestar el flujo completo.
- Resolver o validar el input contractual.
- Llamar al rail de adquisición cuando falten logs.
- Ejecutar preflight.
- Generar el JSON de análisis.
- Renderizar el HTML canónico.
- Convertir a PDF.
- Guardar todos los artefactos localmente.
- Ejecutar postrun.
- Enviar mail por IMAP/SMTP directo si se solicita.

## Contrato de entrada mínimo
```json
{
  "case": {
    "source_channel": "telegram|email",
    "ticket_id": "string|null",
    "request_text": "string"
  },
  "identity": {
    "site": "string|null",
    "building": "string|null",
    "parking_plaza": "string|null",
    "charger_name": "string|null",
    "charger_id": "string|null",
    "ip": "string|null",
    "serial": "string|null",
    "firmware": "string|null"
  },
  "window": {
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD"
  },
  "input_artifacts": {
    "log_zip_path": "string|null",
    "log_zip_url": "string|null"
  },
  "mail": {
    "send_if_applicable": true,
    "recipient": "string|null",
    "subject_hint": "string|null"
  }
}
```

## Contrato de análisis JSON
Dividir en tres capas:

### 1. analysis_core
Contiene datos técnicos y decisión.

Campos mínimos:
- `charger_id`
- `charger_name`
- `site_name`
- `building`
- `parking_plaza`
- `ip`
- `serial`
- `firmware`
- `window_start`
- `window_end`
- `timeline_days` (exactamente 7 elementos)
- `ocpp_flow`
- `metrics`
- `health_score`
- `health_band`
- `health_band_class`
- `service_status`
- `recommended_action`
- `operational_decision_text`
- `client_explanation`
- `probable_cause`
- `evidence_level`
- `remote_actions`
- `remote_events`
- `validation`

### 2. render_context
Contiene variables planas para pintar el HTML sin interpretar logs.

Campos mínimos:
- `remote_site_label`
- `remote_parking_spot`
- `remote_asset_id`
- `remote_location`
- `site_name`
- `health_score`
- `health_band_class`
- `health_band_label`
- `service_status`
- `recommended_action`
- `operational_decision_text`
- `recommended_action_text`
- `timeline_days`
- `ocpp_flow`
- `metrics_bar`
- `affected_layer`
- `evidence_level_label`
- `dominant_finding`
- `probable_cause`
- `client_explanation`
- `remote_actions.available`
- `remote_actions.applied`
- `remote_actions.recommended_next`
- `remote_actions.result`
- `remote_events`
- `evidence_path`

### 3. validation
Controles de calidad.

Campos mínimos:
- `preflight_ok`
- `timeline_days_count`
- `no_demo_values`
- `decision_visible_first_page`
- `actions_humanized`
- `no_exploratory_visit`
- `building_present`
- `plaza_present`
- `output_paths_ok`

## Reglas de validación obligatorias
- `timeline_days` debe tener exactamente 7 elementos.
- `metrics_bar` debe ser coherente con la evidencia.
- No se admiten valores demo.
- La decisión operativa debe verse en la primera página.
- Las acciones remotas deben estar humanizadas.
- No debe aparecer recomendación de visita exploratoria.
- Edificio y plaza deben estar presentes.
- El HTML no interpreta logs: solo pinta el contexto ya resuelto.

## HTML canónico
Usar como fuente única el HTML guardado localmente y aprobado por el usuario.

Ruta canónica actual:
`/home/laia/gridcode-protocol-hub/out/RR-webasto-unite-142-20260612/RR-GC-260612-PLZ142-LABORATORIO.html`

Reglas:
- No cambiar la base visual salvo correcciones explícitas.
- No usar una variante para preview y otra para PDF.
- El título del cuerpo debe usar la fuente del texto principal, no la de marca.
- El footer y el logo deben permanecer canónicos.

## PDF canónico
- Generado con WeasyPrint desde el mismo HTML fuente.
- `base_url` debe apuntar al directorio del HTML para resolver assets locales.
- El logo debe resolverse desde ruta local absoluta o relativa dentro del mismo directorio del HTML.

## Artefactos de salida
- `analysis.json`
- `report.html`
- `report.pdf`
- `evidence/`
- `log.zip`
- `mail/` (solo si aplica)

## Ruta de salida recomendada
`/home/laia/gridcode-protocol-hub/out/webasto-unite-analysis/<case_id>/`

Dentro de esa carpeta:
- `analysis.json`
- `report.html`
- `report.pdf`
- `log.zip`
- `evidence/`
- `mail/`

## Flujo de mail
- Gestión por IMAP/SMTP directo.
- No usar Gmail UI.
- Aplicar `email-style-grid-code` antes de emitir.
- Enviar solo si el caso lo requiere.

## Comando único propuesto
```bash
python3 scripts/run_webasto_unite_log_analysis_v1.py \
  --input /path/to/input.json \
  --output /home/laia/gridcode-protocol-hub/out/webasto-unite-analysis/<case_id>/
```

## Salida esperada del runner
```json
{
  "status": "ok",
  "case_id": "string",
  "analysis_json": "/path/to/analysis.json",
  "html": "/path/to/report.html",
  "pdf": "/path/to/report.pdf",
  "log_zip": "/path/to/log.zip",
  "evidence_dir": "/path/to/evidence",
  "mail_sent": true,
  "mail_transport": "imap_smtp_direct",
  "postrun_ok": true
}
```

## Regla de oro
La única creatividad permitida está en el análisis del log y el dictamen técnico.
Todo lo demás debe permanecer contractual, determinista y repetible.
