# Guía oficial — Form-OnsiteS (Reporte de Verificación Onsite)

Fuente: requerimiento validado de operación (Dario) recibido el 2026-05-07.

## 1) Precompletado automático (NO editable por técnico)
Estos campos deben venir poblados desde ticket + análisis remoto y bloquearse en el PDF:

- Ticket ID
- Fecha de visita (si viene de sistema; si no, editable)
- Requirente / Cliente
- Servicio
- Cargador (ID/nombre)
- Ubicación
- Nº plaza / referencia
- RFID de prueba propuesta
- IP del cargador
- Modelo / serie (si se conoce)
- Resumen del motivo de intervención
- Camino del ticket / ruta de gestión (pasos 1-5)

## 2) Choices interactivos obligatorios (checklist)
Cada fila del checklist debe tener campos interactivos:

- Estado: `OK | No OK | No verificable`
- Resultado: depende del punto de control
- Requiere acción: `Sí | No`

Puntos de control base:
- Energización general
- Conectividad/ping
- Estado físico
- Manguera/conector
- Bloqueo/servo
- Lectura RFID
- Tipo de autorización
- Inicio sesión
- Continuidad
- Cierre

## 3) Choices interactivos (bloque final)
- Resultado principal de la visita:
  - Operativo OK
  - Operativo con observaciones
  - Falla confirmada
  - Sin visibilidad suficiente
  - Requiere escalado

- Causa probable dominante:
  - Problema local del cargador
  - Problema de comunicación
  - Problema de autorización (RFID/backend)
  - Problema mecánico (manguera/servo/bloqueo)
  - Externalidad del sitio
  - No concluyente

- Siguiente paso recomendado:
  - Cerrar ticket
  - Seguimiento remoto
  - Escalar a soporte backend
  - Programar intervención correctiva
  - Requiere repuesto
  - Requiere nueva visita

## 4) Texto editable (open fields)
- Observación corta por fila (1 línea)
- Observación técnica del técnico (multilínea)
- Aprobación onsite:
  - Persona autorizante
  - Cargo/relación
  - Firma/validación

## 5) Evidencia fotográfica
Cuadros fijos en diseño (no obligatorio como form text):
- Foto 1 – Vista general del cargador
- Foto 2 – Display / LEDs / error
- Foto 3 – Conector / manguera / bloqueo
- Foto 4 – Evidencia adicional

Opcional: campo corto editable para comentario por foto.

## 6) Comportamiento esperado
- PDF precompletado con datos de sistema
- Header/footer corporativos inmutables
- Checklist marcado en <2 minutos
- Campos abiertos mínimos y claros
- Entregable guardable/enviable con fotos
