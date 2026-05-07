# Vista de negocio — Operación SLA Colonial (v1)

Este documento traduce la arquitectura técnica a impacto de negocio, evitando foco de backend.

## Meta de negocio
- Reducir visitas onsite innecesarias.
- Acelerar respuesta al cliente con evidencia objetiva.
- Aumentar consistencia de reportes para auditoría y renovación SLA.

## Nota estratégica
Este rail no se gobierna por metas de KPI fijas. La operación se ejecuta según demanda real de tickets y verificaciones preventivas requeridas por SLA. El foco es consistencia, evidencia y decisión correcta (remoto vs onsite) por caso.

## Estrategia por grupo
- Grupo 1 (ticket): mantener estable, no intervenir.
- Grupo 2 (remoto): convertir en principal motor de resolución.
- Grupo 3 (onsite): usar cuando aporta valor real o cuando remoto no es viable.

## Regla ejecutiva
- “Si se puede resolver en remoto con evidencia, no mover técnico.”
- “Si no hay certeza remota o criticidad alta, escalar onsite rápido.”

## Evidencias para decisión comercial
- Reporte remoto uniforme por cargador.
- Reporte onsite uniforme por visita.
- Registro de evidencias (logs/fotos) trazable por ticket.

## Beneficio esperado
- Menor costo operativo por desplazamientos.
- Mayor confianza del cliente por consistencia documental.
- Mejor previsibilidad del SLA y de la carga del equipo técnico.
