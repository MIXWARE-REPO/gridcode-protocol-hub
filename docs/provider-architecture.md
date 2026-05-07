# Arquitectura de Proveedores (Inbox + Contactos)

Objetivo: desacoplar reglas de negocio (motor Python) del proveedor externo (Google API).

## Principio

- Motor Python (protocolos): decide prioridad, estado, SLA, aprendizaje.
- Provider Adapter (Google/otro): solo integra lectura/escritura externa.

## Interfaces base

Definidas en `shared/contracts/providers.py`:

1. `InboxProvider`
- `fetch_inbox(limit)`
- `fetch_thread(thread_id)`
- `send_reply(thread_id, subject, body, to, cc)`

2. `ContactProvider`
- `find_contact(email)`
- `create_contact(payload)`
- `minimal_update_contact(contact_id, payload)`
- `full_update_contact(contact_id, payload)`

3. `AttachmentProvider`
- `list_message_attachments(message_id)`
- `fetch_attachment_bytes(message_id, part_id)`
- `upload_to_drive(filename, content, folder_id)`
- `resolve_drive_file(drive_file_id)`

## Flujo recomendado

1) InboxProvider trae mails.
2) Motor procesa (read -> interpret -> write -> validate).
3) Si corresponde, InboxProvider envía respuesta.
4) Si hay update de contacto, ContactProvider ejecuta acción.
5) Learning rail registra outcome.

## Ventaja

- Si cambia Google API, solo cambia el adaptador.
- Protocolos y reglas de negocio no se tocan.
- Test unitarios se hacen con providers mockeados.
