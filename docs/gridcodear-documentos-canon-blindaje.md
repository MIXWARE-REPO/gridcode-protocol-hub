# Gridcodear Documentos — Canon blindado

## Estado
Este documento fija la convención canónica de `gridcodear-documentos` y blinda su uso como troncal Grid Code para documentos A / T / C.

## Regla de blindaje del código visible en el header
El badge del header solo puede mostrar un identificador corto de familia + número + punto.

Formato aprobado:
- `T--GC-YYYYMMDD-VN`
- `A--GC-YYYYMMDD-VN`
- `C--GC-YYYYMMDD-VN`

## Reglas obligatorias
- La familia va primero: `T`, `A` o `C`.
- Luego doble guion.
- Luego `GC`.
- Luego la fecha `YYYYMMDD`.
- Luego la versión `VN` (por ejemplo `V1`).
- No usar `IAP`.
- No incluir títulos, asuntos ni texto libre en el badge.
- El badge debe permanecer corto y dentro del área imprimible.
- Si el valor no cabe o no cumple patrón, se normaliza antes del render.

## Regla de nombre de archivo / PDF
Formato aprobado:
- `T-GC-YYYYMMDD-VN-CLIENTE`
- `A-GC-YYYYMMDD-VN-CLIENTE`
- `C-GC-YYYYMMDD-VN-CLIENTE`

Reglas:
- El nombre del cliente va al final.
- El nombre del cliente va en MAYÚSCULAS.
- El título del archivo no sustituye al código del header.
- El header y el archivo son dos identificadores distintos.

## Ejemplo canónico
- Header: `T--GC-20260609-V1`
- Archivo: `T-GC-20260609-V1-HIDRICA GROUP`

## Propósito
Evitar desbordes en el esquema imprimible y mantener una separación limpia entre:
- código visible del documento,
- título del informe,
- nombre técnico del archivo.
