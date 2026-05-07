# Recovery note — Base oficial de reporte agregado

Fecha: 2026-05-07

## Hallazgo
- La skill `gridcode-aggregated-behavior-remote-analysis` exige usar como base:
  `/home/laia/.hermes/cache/documents/reporte_remoto_base_oficial.pdf`
- En el entorno no existía ese archivo con ese nombre.
- Sí existía la versión aprobada enviada por usuario:
  `/home/laia/.hermes/cache/documents/doc_5c5a5f94b7b9_muestra_reporte_analisis_agregado_base (1).pdf`

## Acción aplicada
- Se restauró/normalizó la base oficial copiando el archivo aprobado a:
  `/home/laia/.hermes/cache/documents/reporte_remoto_base_oficial.pdf`

## Regla operativa
- Cualquier generación futura de "análisis agregado" debe partir de esta base oficial.
- Prohibido generar layout alternativo en HTML si el usuario pide continuidad visual.
- Para personalización, solo se modifican campos dinámicos de contenido.
