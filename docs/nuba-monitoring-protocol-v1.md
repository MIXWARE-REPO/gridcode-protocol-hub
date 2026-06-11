# NUBA Monitoring Protocol v1

## Identidad
- Plataforma: NUBA (cloud)
- Propósito: validar, controlar, monitorizar y gestionar múltiples instancias desde una única plataforma.

## Acceso
- URL: `https://nuba.grid.touch`
- Usuario operativo: `laia@grid.touch`
- Rol esperado: `super administrador`

## Jerarquía operativa
1. Clusters
2. Nodos dentro de cada cluster

## Zona crítica: Administración
Desde Administración se puede:
- Ver todas las instalaciones montadas sobre NUBA.
- Filtrar instalaciones por creador.
- Entrar al detalle de cada instancia.

## Caso de ejemplo enseñado
- Filtro por creador: `Alex Rojas (Grupo Noria)`
- Instancia detectada: `Noria Global`
- Estructura observada:
  - cluster `Noria Global`
  - dos nodos (uno OFF y uno ON)

## Señales y lectura funcional
- Nodo OFF: requiere atención/diagnóstico.
- Nodo ON: instancia funcional.
- En nodo funcional se revisa:
  - cantidad de cargadores
  - usuarios habilitados
  - sesiones (con filtrado)
  - backups
  - configuraciones (connections / energy / system)

## Teleport Support (T)
- Indicador `T` activo => Teleport habilitado.
- Acción: `Teleport Support` abre acceso directo a la instancia para soporte.
- Uso: diagnóstico rápido cuando la instancia no responde por flujo normal.

## Patrón de incidencia enseñado
- Dashboard inactivo en instancia => cliente probablemente no puede ingresar por vía normal.
- Implica intervención técnica sobre la instancia.

### Procedimiento normal ante dashboard inactivo
1. Ingresar por `Teleport Support` (si `T` está activo).
2. Ejecutar reinicio preventivo de servicios de la instancia.
3. Verificar si el dashboard levanta.
4. Observar estabilidad: puede levantar y volver a caer (flapping).
5. Registrar hallazgo de existencia/estado:
   - activo estable
   - activo inestable (cae)
   - inactivo persistente

### Lectura operativa
- Si tras el reinicio el dashboard intenta activarse, confirma que el acceso por Teleport permite intervención efectiva.
- Si vuelve a caer, hay incidencia subyacente de servicios que requiere diagnóstico adicional.

## Vista dentro de instancia (health operativo)
En una instancia se monitorean 3 softwares principales en ejecución:
1. motor/algoritmo DLM
2. solution/backend operativo
3. interfaz dashboard

Además:
- seguimiento de errores de instancia para trazabilidad de incidentes
- verificación de estado de ejecución y caídas

## Administración global en NUBA
En la zona de Administración se gestiona:
1. Instancias
2. Managers (alta/edición)
3. Usuarios de plataforma por rol:
   - user
   - admin
   - super admin
4. Usuarios EV (carga de vehículo)
5. Licencias activas

## Gestión de códigos de activación, licencias y módulos

### Modelo funcional (clave)
1. El software nace con `código de activación` (canjeo), no con licencia activa.
2. Solo al canjear en NUBA, el código se convierte en licencia.
3. Esto evita duplicación: un mismo código no puede generar dos licencias.

### Estados de códigos
- `No canjeado`:
  - editable
  - se pueden ajustar módulos/metadata antes del canje
- `Canjeado`:
  - ya convertido en licencia
  - no editable en términos de redefinir su naturaleza original

### Validación recurrente
- Con operación online, el sistema revalida licencia periódicamente (referencia operativa: cada 7 días).
- Sirve para control de consistencia/licenciamiento y anti-duplicación.
- Puede desacoplarse puntualmente para contingencia, pero operación normal recomendada: validación conectada y auditable.

### Creación de código de activación (flujo)
1. Definir descripción completa (producto/alcance).
2. Elegir producto objetivo (ej. Plus).
3. Seleccionar módulos activos (ejemplos vistos: User Manager, Backups, DC).
4. Definir estado del código/licencia: `activo` o `inactivo`.
5. (Opcional y poco frecuente) configurar fecha de expiración.
6. `Save`.
7. Copiar código generado para procedimiento de validación en instancia.

### Gestión de licencias y módulos por instancia
- revisar plan/licencia vigente
- revisar módulos activos
- habilitar/deshabilitar módulos según política

## Checklist de diagnóstico mínimo
1. Login en NUBA.
2. Ir a Administración.
3. Filtrar por creador/cliente.
4. Validar estado cluster/nodos (ON/OFF).
5. Revisar cargadores/usuarios/sesiones/backups.
6. Revisar settings (connections/energy/system).
7. Si `T` activo, abrir Teleport Support y validar estado real.
8. Confirmar si dashboard está activo/inactivo.
9. Si está inactivo: reinicio preventivo de servicios + revalidación de estabilidad.
10. Verificar estado de los 3 servicios base y errores de instancia.
11. Verificar licencia, validación recurrente y módulos activos.
