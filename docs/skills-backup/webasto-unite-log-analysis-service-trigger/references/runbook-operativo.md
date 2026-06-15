# Runbook Operativo — Webasto Unite Log Analysis Service Trigger

## Entrada
- Telegram o mail interno válido.
- Si hay un único dato, resolver identidad en Supabase.
- Si hay dos datos consistentes, procesar directo.
- Si el IP empieza por 192.*, se activa el rail de adquisición de logs por Playwright.

## Orden de ejecución
1. Identificar cargador.
2. Clasificar red.
3. Descargar logs.
4. Preflight.
5. Generar analysis.json.
6. Renderizar report.html.
7. Convertir a report.pdf.
8. Guardar localmente.
9. Postrun validation.
10. Mail por IMAP/SMTP directo solo si aplica.

## Reglas rígidas
- No reutilizar contexto de corridas previas.
- No inventar identidad del cargador.
- No variar el HTML base sin pedido explícito.
- No usar Gmail UI.
- No recomendar visita exploratoria.
- Timeline de 7 días exactos.
- La creatividad solo vive en el dictamen técnico.