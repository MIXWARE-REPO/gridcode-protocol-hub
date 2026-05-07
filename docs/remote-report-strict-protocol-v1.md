# Protocolo estricto de emisión de reporte remoto (v1)

Objetivo: emitir SIEMPRE el mismo reporte (misma plantilla), cambiando solo datos del caso.

## Regla de invariancia
- Prohibido rediseñar PDF.
- Prohibido overlays libres.
- Solo rellenar campos existentes en plantilla validada.

## Implementación
- `reports/remote_report_strict_v1.py`
- `scripts/generate_remote_report.py`

## Inputs obligatorios
- template (PDF validado)
- output (PDF final)
- data-json (datos del caso)

## Campos mínimos de datos
- ticket_id
- charger_id
- charger_ip
- site_name
- endpoint_before
- endpoint_target
- endpoint_after
- endpoint_saved
- last_charge_at_cet
- last_charge_duration
- idtag_used
- free_mode_detected
- charge_result
- log_zip_name
- log_zip_bytes

## Ejecución
```bash
python3 scripts/generate_remote_report.py \
  --template /ruta/plantilla-validada.pdf \
  --output /ruta/salida/reporte.pdf \
  --data-json /ruta/caso.json
```

## Validación de negocio
- Si `idtag_used` contiene `#freecharging`, marcar `free_mode_detected=true`.
- Si `endpoint_after != endpoint_target`, reporte debe indicar cambio NO persistido.
- Horarios de actividad siempre en CET/CEST.
