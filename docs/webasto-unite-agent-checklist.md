# Webasto/Unite Agent Checklist

Objetivo: que el agente siempre siga el mismo camino, sin depender de memoria contextual.

## 1) Identificar el cargador
Fuente canónica:
- `website/docs/reference/supabase-charger-registry-schema.sql`

Regla:
- 1 dato -> verificar.
- 2 datos -> confrontar.
- Si no es unívoco -> bloquear y pedir el dato mínimo faltante.

## 2) Clasificar la red por IP
| IP | Red | Conexión | Camino |
|---|---|---|---|
| `10.x.x.x` | COLONIAL | VPN | `colonial-vpn-charger-access` |
| `192.168.31.x` | Laboratorio | Directa | runner Playwright directo |

## 3) Elegir la acción
- Cambio de ID -> runner Playwright específico.
- Cambio de endpoint OCPP -> runner Playwright específico.
- Descarga de log de eventos -> runner Playwright específico.
- Firmware update -> fuera del happy path hasta tener runner dedicado.

## 4) Ejecutar
- No tocar UI hasta tener identidad + red resueltas.
- Si es COLONIAL, conectar primero por VPN.
- Si es laboratorio, conectar directo.
- Usar el runner específico de la acción.

## 5) Verificar
- Guardar / descargar.
- Reentrar o validar persistencia.
- Confirmar evidencia real.

## 6) Fallback
- Snapshots solo como fallback documentado de diagnóstico o drift.
- No usar snapshot por pereza ni por pérdida de contexto.

## 7) Fuentes de verdad
- Runbook: `docs/runbook-colonial-ocpp-webasto-unite-v1.md`
- Contrato: `docs/webasto-unite-control-contract.md`
- Input contract: `docs/webasto-unite-input-contract.md`
- VPN Colonial: `productivity/colonial-vpn-charger-access/SKILL.md`
- Schema cargadores: `website/docs/reference/supabase-charger-registry-schema.sql`
- Control script: `scripts/webasto_unite_control_contract.py`

## Resultado esperado del agente
Siempre debe responder con:
- cargador identificado,
- red clasificada,
- vía de conexión elegida,
- runner elegido,
- verificación esperada,
- evidencia generada,
- bloqueos si falta algo.
