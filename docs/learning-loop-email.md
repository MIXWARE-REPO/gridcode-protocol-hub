# Learning Loop — Email (P1/P2)

Objetivo: capturar aprendizaje real de respuestas para mejorar consistencia y calidad.

## Qué se guarda por cada caso

- timestamp
- canal (email)
- prioridad (p1/p2)
- tópico
- resumen del requerimiento
- mensaje de coordinación generado
- input estratégico de Dario
- respuesta final enviada al cliente
- resultado observado (pending / respondio_ok / sin_respuesta / pidio_ajuste / cerrado_por_otro_canal)
- notas de mejora

## Formato recomendado (JSONL)

Archivo: `data/email_learning_log.jsonl`

Un registro por línea:

```json
{"timestamp":"2026-05-07T11:00:00Z","channel":"email","priority":"p1","topic":"garantía cargador","request_summary":"cliente solicita confirmación de visita","assist_message":"Me llegó un mail...","dario_input":"decirle semana próxima","final_reply":"Buenas Victor...","outcome":"respondio_ok","improvement_note":"mantener cierre breve"}
```

## Regla operativa

1. Leer y filtrar el mail entrante.
2. Enrutar por camino según remitente/destinatarios (P1/P2).
3. Pedir enfoque a Dario cuando sea P1.
4. Redactar y enviar respuesta.
5. Registrar caso en JSONL.
6. Gestionar estado pendiente/cerrado.
7. Generar snapshot semanal de pendientes para proceso de reportes.

Resultado operativo: lectura, filtros, caminos por remitente y cambios de estado gestionados.

## Uso del aprendizaje

- Afinar plantillas por tipo de tópico.
- Mejorar precisión de tono y cierre.
- Reducir iteraciones de ida y vuelta para respuestas frecuentes.
