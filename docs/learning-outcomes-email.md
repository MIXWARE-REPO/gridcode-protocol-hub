# Catálogo de outcomes — Email Learning Rail

Este documento define el significado operativo de cada outcome permitido en el learning rail de email.

## Outcomes válidos

1) pending
- Significa: caso registrado pero aún sin resolución final observada.
- Cuándo usarlo: inmediatamente después de preparar/enviar respuesta y todavía sin feedback final.

2) respondio_ok
- Significa: el cliente respondió de forma favorable o quedó confirmada la gestión esperada sin ajustes.
- Cuándo usarlo: cuando la interacción confirma avance correcto.

3) sin_respuesta
- Significa: no hubo respuesta del cliente dentro de la ventana de seguimiento definida.
- Cuándo usarlo: al vencer el plazo de espera sin novedades.

4) pidio_ajuste
- Significa: el cliente pidió corrección, aclaración o cambio sobre la respuesta enviada.
- Cuándo usarlo: cuando la respuesta inicial no cerró el requerimiento y requiere nueva iteración.

5) cerrado_por_otro_canal
- Significa: el tema se resolvió fuera del hilo de email (teléfono, chat, reunión u otro canal).
- Cuándo usarlo: cuando se confirma cierre operativo externo al correo.

## Regla de normalización

Si se intenta registrar un outcome fuera de este catálogo, el rail lo normaliza automáticamente a `pending` para mantener consistencia de datos.
