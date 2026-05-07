# Estructura de Actualización de Contactos

Objetivo: estandarizar cómo se decide y aplica actualización de contactos.

## Estados de acción (ya definidos en protocolo)

- `create`
- `minimal_update`
- `full_update`
- `skip`

## Contrato de decisión (salida del protocolo)

Campos clave:
- `action`: una de las 4 acciones.
- `reason_codes`: lista de razones de negocio.
- `contact_payload`: datos sugeridos para persistir.

## Payload base recomendado

```json
{
  "primary_email": "cliente@empresa.com",
  "display_name": "Nombre Cliente",
  "organization": "Empresa",
  "phone": "+34...",
  "tags": ["gridcode", "email"],
  "last_topics": ["garantía", "seguimiento comercial"],
  "tone_preference": "formal",
  "relationship_level": "known|new|strategic",
  "last_interaction_at": "2026-05-07T10:00:00Z",
  "notes": "Resumen corto contextual"
}
```

## Regla de aplicación

1. `create`:
- si no existe contacto por email.

2. `minimal_update`:
- contacto existe, solo cambia contexto ligero
  (last_topics, last_interaction_at, notes cortas, tags menores).

3. `full_update`:
- cambios relevantes de identidad/organización/segmento/rol.

4. `skip`:
- correo irrelevante (ej. cc_only sin aporte) o sin datos nuevos útiles.

## Matriz rápida decisión

- Nuevo remitente + señal operativa -> `create`
- Remitente conocido + nuevo hilo similar -> `minimal_update`
- Cambio de empresa/rol/canal estratégico -> `full_update`
- Notificación sin valor de contexto -> `skip`

## Reglas de calidad

- Nunca borrar información crítica existente sin evidencia.
- Priorizar append/merge sobre overwrite.
- Registrar `reason_codes` siempre.
- Toda actualización debe quedar trazable en learning/log.
