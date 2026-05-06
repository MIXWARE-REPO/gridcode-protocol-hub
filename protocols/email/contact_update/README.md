# email_contact_update_v1

Para qué sirve:
- Decide cómo actualizar la ficha de contacto después de leer/contextualizar un mail.
- Mantiene el contexto vivo en Google Contacts sin meter ruido.

Qué hace:
1) Recibe estado del contacto actual.
2) Recibe contexto calculado por `email_contact_context_v1`.
3) Decide acción: `create`, `minimal_update`, `full_update` o `skip`.
4) Devuelve payload estandarizado para guardar.

Cómo se usa:
- Entrada: `contact` + `context` + `email` + `policy`.
- Salida: `action`, `reason_codes`, `update_payload`.
- Si `action=skip`, no se persiste nada.

Tags:
- email
- contacts
- google-contacts
- context
- update
- pending
- relationship

Input esperado (resumen):
- `contact`: ficha actual del contacto (si existe)
- `context`: salida del protocolo de contextualización
- `email`: estado de mail actual (incluye status, is_cc_only)
- `policy`: límites de actualización (ej: max_topics)

Output esperado (resumen):
- `action`: create|minimal_update|full_update|skip
- `reason_codes`: lista de motivos
- `update_payload`: campos finales para persistir
- `expected_store`: google_contacts

