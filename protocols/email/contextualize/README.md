# email_contact_context_v1

Qué hace:
- Toma un mail entrante y contextualiza el contacto por remitente e historial.
- Si el asunto es nuevo, igual busca relación previa por remitente.
- Devuelve nivel de contexto, tono sugerido y últimos 3 temas.
- Marca si corresponde actualizar Google Contacts y si entra a cola de pendientes.

Ejecuciones clave:
1) Verifica remitente conocido.
2) Verifica si es primer mail del hilo.
3) Detecta relación previa por historial, aunque cambie el asunto.
4) Sugiere tono (formal/neutral/fresh) por comportamiento previo.
5) Resume últimos 3 temas activos del contacto.

Keywords:
- email
- contexto
- remitente
- historial
- tono
- google-contacts
- pending
- gridcode

Notas:
- Este bloque no responde mails.
- Este bloque prepara contexto para los bloques de interpretación y escritura.
