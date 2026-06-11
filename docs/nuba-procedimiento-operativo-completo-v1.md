# NUBA — Procedimiento Operativo Completo v1

## Objetivo
Estandarizar operación en NUBA para:
- monitoreo de instancias
- diagnóstico de estado
- soporte por Teleport
- gestión de códigos de activación/licencias/módulos

---

## 1) Acceso y rol
- URL: https://nuba.grid-code.tech
- Usuario operativo: Laia@grid-code.tech
- Rol esperado: Super Admin

Login validado en runtime (Playwright):
- input usuario: `input[name="username"]`
- input contraseña: `input[name="password"]`
- submit: botón `SUBMIT`

---

## 2) Estructura funcional de NUBA
NUBA permite validar/controlar/monitorizar/gestionar múltiples instancias desde una plataforma cloud única.

Jerarquía:
1. Clusters
2. Nodos dentro de cada cluster

Zonas principales:
- Dashboard
- Admin Zone
- My User Keys
- Support

---

## 3) Admin Zone: dominios operativos
En Admin Zone se gestionan:
- Clusters
- Managers
- EV Users
- Licenses
- Activation Codes

En una instancia se supervisan 3 software base:
1. DLM (algoritmo)
2. Solution/backend
3. Dashboard UI

Además, seguimiento de errores para trazabilidad.

---

## 4) Diagnóstico de incidencia: dashboard inactivo
Flujo estándar:
1. Abrir instancia afectada.
2. Si `T` (Teleport) está activo, usar Teleport Support.
3. Reiniciar servicios preventivamente.
4. Verificar si dashboard levanta.
5. Clasificar estado:
   - activo estable
   - activo inestable (flapping)
   - inactivo persistente

Regla:
- Si levanta tras reinicio, el bypass de soporte funciona.
- Si vuelve a caer, hay falla subyacente de servicios.

---

## 5) Licencias y códigos de activación
Modelo:
- El software nace con código de activación (canjeo), no con licencia activa.
- Al canjear en NUBA, se convierte en licencia.
- Un código no puede generar dos licencias (anti-duplicación).

Estados:
- No canjeado: editable.
- Canjeado: ya convertido en licencia.

Validación recurrente:
- Referencia operativa: revalidación periódica online (ej. cada 7 días).
- Recomendado: mantener conectada y auditable.

---

## 6) Crear código de activación (flujo real validado)
Ruta:
1. Admin Zone
2. Activation Codes
3. Botón `+` flotante abajo derecha

Selector del botón `+` validado:
- `div.fixed.right-0.bottom-0.rounded-full.cursor-pointer`

Formulario detectado tras pulsar `+`:
- descripción: input con placeholder tipo `Write a description here`
- producto: `select` con opciones observadas:
  - EVA
  - PLUS
  - IRIS
  - WINGS
- acción final: botón `SAVE`

Regla de negocio:
- Normalmente se define estado activo/inactivo.
- Expiración por fecha es opcional y poco frecuente.

Resultado esperado:
- aparece el nuevo código en listado Activation Codes
- estado inicial habitual: Not redeemed

Ejemplo real generado:
- `plus-0aafe7c969d046ce-347` (Not redeemed)

---

## 7) Checklist operativo de auditoría
1. Login correcto.
2. Entrar a Admin Zone.
3. Verificar tabs de gestión (Clusters/Managers/EV Users/Licenses/Activation Codes).
4. Validar estado cluster/nodos ON/OFF.
5. Revisar salud de servicios (DLM/Solution/Dashboard) y errores.
6. En incidencias, usar Teleport si está disponible.
7. En licencias, validar estado canjeado/no canjeado.
8. Crear código de activación cuando aplique y confirmar aparición en lista.
9. Registrar código generado + descripción + estado.

---

## 8) Scripts asociados (automatización)
- Orquestador NUBA:
  - `shared/orchestration/nuba_playwright_v1.py`
- Runner NUBA:
  - `scripts/run_nuba_playwright_v1.py`

Corrida de creación verificada en esta sesión:
- output summary:
  - `out/nuba_activation_create_summary.json`
- evidencia runtime:
  - `out/nuba-playwright/<timestamp>_nuba/`

---

## 9) Criterio de “listo para producción”
Se considera listo cuando:
- login + navegación admin son estables
- selector del `+` y `SAVE` funcionan consistentemente
- creación de código queda reflejada en tabla final
- evidencia queda guardada en JSON + capturas
- no hay dependencia de texto ambiguo en botones
