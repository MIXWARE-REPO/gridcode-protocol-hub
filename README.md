# gridcode-protocol-hub

Biblioteca modular de protocolos deterministas para skills de IA.

## Objetivo
Estandarizar flujos en microprotocolos (input -> output) con validación bloqueante, versionado y trazabilidad.

## Principios
- Determinismo: mismo input, mismo output.
- Orquestación: la skill coordina, el protocolo ejecuta.
- Validación dura: si no cumple contrato, falla.
- Gobernanza: cambios por branch + tests + revisión.

## Estructura
- `protocols/`: microprotocolos por dominio/stage
- `shared/contracts/`: contratos comunes
- `tests/`: unit + golden
- `docs/`: arquitectura y políticas
- `PROTOCOL_INDEX.yaml`: índice maestro de búsqueda
