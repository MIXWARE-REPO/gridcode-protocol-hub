# Reporte remoto tipo dashboard (HTML/PDF) — protocolo estricto v1

Objetivo: salida siempre igual, visual clara tipo dashboard, con campos fijos y lectura rápida.

Arquitectura:
- Schema fijo: `reports/remote_report_dashboard_schema_v1.py`
- Template visual único: `reports/templates/remote_dashboard_v1.html.j2`
- Renderer: `reports/remote_report_dashboard_renderer_v1.py`
- Script CLI: `scripts/generate_remote_dashboard_report.py`

Reglas estrictas:
1) Un único template aprobado.
2) Campos fijos (no se agregan/quitan por corrida).
3) Validación de schema previa obligatoria.
4) Horarios en CEST/CET.
5) Interpretación estándar: `#freecharging` => modo Free.

Ejecución:
python3 scripts/generate_remote_dashboard_report.py \
  --data-json examples/remote_dashboard_case.json \
  --output-html out/remote_dashboard.html \
  --output-pdf out/remote_dashboard.pdf

Nota de negocio:
- Este formato no reemplaza la plantilla contractual si hay obligación legal de formato.
- Se usa como reporte ejecutivo de lectura rápida, consistente y comparable.
