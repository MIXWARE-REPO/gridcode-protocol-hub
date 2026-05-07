# Form Templates Registry (Grid Code)

Este directorio es la fuente única de plantillas HTML aprobadas para reportes.

## Ubicaciones oficiales

- Form-RemoteS (análisis remoto agregado):
  - `templates/forms/form-remotes/v1/template.html`

- Form-OnsiteS (servicios onsite):
  - `templates/forms/form-onsites/v1/template.html`

- Form-Preliminar (análisis preliminares):
  - `templates/forms/form-preliminar/v1/template.html`

## Regla de integración

- El protocolo Python debe leer SIEMPRE desde estas rutas.
- Prohibido usar HTML embebido en código para estos 3 reportes.
- Versionado por carpeta `vN`.

## Flujo de actualización

1. Subir/commit del HTML en su ruta correspondiente.
2. No tocar nombres de campos sin actualizar contrato de datos Python.
3. Validar render HTML->PDF y estructura.
