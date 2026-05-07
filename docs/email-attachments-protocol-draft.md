# Protocolo de Adjuntos (draft) — Email + Drive

Estado: borrador operativo (listo para integrar con provider Google).

## Objetivo
Que el motor Python sepa SIEMPRE de dónde obtener adjuntos, aunque la ruta final aún evolucione.

## Fuentes canónicas (orden de búsqueda)
1. Adjuntos nativos de Gmail (attachmentId en partes del mensaje).
2. Links de Google Drive dentro del cuerpo del mail.
3. Resolución directa por Drive API (fileId conocido).

## Regla de decisión
- Si hay adjunto Gmail: usar fuente 1 como primaria.
- Si no hay adjunto pero hay link Drive: usar fuente 2 y resolver fileId.
- Si llega referencia externa de fileId: usar fuente 3.

## Custodia y trazabilidad
- Política default Drive habilitada.
- Carpeta sugerida: GridCode/EmailAttachments/Inbox.
- Guardar naming trazable: {date}_{sender}_{subject}_{filename}.
- Registrar referencia en learning/log para seguimiento.

## Contratos Python
- `shared/contracts/attachments.py`
  - AttachmentRef
  - AttachmentProvider

- `shared/orchestration/email_attachments_router_v1.py`
  - detect_attachment_sources(email_record)
  - build_attachment_resolution_plan(email_record, category)

## Nota
Este protocolo define el "de dónde tirar" y el orden de resolución. La implementación concreta de credenciales/rutas de Drive se integra en el adapter Google del provider, no en la lógica de negocio.
