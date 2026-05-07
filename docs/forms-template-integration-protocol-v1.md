# Protocolo de integración de plantillas HTML (v1)

Objetivo: integrar 3 plantillas base estables para reportes, con búsqueda determinista por ruta.

## Plantillas oficiales

1) Form-RemoteS
- Uso: análisis de logs de eventos / comportamiento agregado remoto
- Ruta: `/home/laia/gridcode-protocol-hub/templates/forms/form-remotes/v1/template.html`

2) Form-OnsiteS
- Uso: reportes de servicios onsite
- Ruta: `/home/laia/gridcode-protocol-hub/templates/forms/form-onsites/v1/template.html`

3) Form-Preliminar
- Uso: reportes preliminares
- Ruta: `/home/laia/gridcode-protocol-hub/templates/forms/form-preliminar/v1/template.html`

## Contratos Python esperados

- Cada plantilla debe tener contrato de datos explícito en `reports/`.
- El renderer carga archivo HTML de ruta fija + datos del contrato.
- Render a PDF con pipeline único.

## Convención de campos

- Campos dinámicos deben identificarse con placeholders estables (ej. `{{ ticket_id }}`, `{{ endpoint_after }}`).
- No cambiar nombres de placeholder sin migración de contrato.

## Publicación

- Commit en rama de trabajo y merge a `main`.
- La ruta oficial no cambia entre corridas.

## Nota de carga de archivos

- El chat no acepta `.html` como adjunto.
- Subir el HTML al repositorio GitHub en las rutas oficiales y avisar commit/branch para integración.
