# Charger WebUI Learning Procedure v1 (captura guiada)

## Contexto de laboratorio
- Los cargadores se identifican por los 3 últimos dígitos de su IP.
- Acceso estándar:
  - Usuario: `sanmin`
  - Contraseña: obtenida desde base de datos (no hardcodear).

## Alcance permitido en esta fase
Solo operar en:
1. OCPP Settings
2. Network Interfaces
3. System Maintenance

No operar en:
- Local/Load (bloqueado por política operativa)
- Cualquier tab fuera de alcance explícito

---

## Bloque 1: OCPP Settings (cambio de endpoint + política Free Charge)

### Aclaración crítica de campo
- El campo que se configura en `true/false` es `Free Charge Mode Active` (modo de carga libre).
- Comportamiento:
  - Si `Free Charge Mode Active = true`, el cargador puede autorizar carga localmente a cualquiera que conecte, incluso si backend no autoriza.
  - Si `Free Charge Mode Active = false`, con OCPP activo se fuerza la lógica de autorización gestionada por backend.

### Regla operativa obligatoria
- Siempre que se use endpoint OCPP para que el backend gestione autorizaciones de usuarios:
  - `Free Charge Mode Active` debe quedar en `false`.


### Objetivo
Cambiar endpoint OCPP del cargador para redirigir comunicación WebSocket al host/puerto objetivo.

### Variables
- `charger_id_last3`: identificador operativo del cargador (3 últimos dígitos IP)
- `ocpp_endpoint_target`: endpoint objetivo
- `ocpp_port_target`: puerto objetivo
- `expected_endpoint`: valor final persistido

Valores del caso enseñado:
- `ocpp_endpoint_target = 192.168.31.166`
- `ocpp_port_target = 2880`
- `expected_endpoint = 192.168.31.166:2880`

### Pasos observados
1. Entrar al cargador en WebUI local.
2. Ir a `OCPP Settings`.
3. Verificar que se está editando el ID/cargador correcto.
4. Modificar `Endpoint OCPP` a `192.168.31.166:2880`.
5. Ejecutar `Save`.
6. Esperar a que el guardado impacte (la UI vuelve a pantalla principal).

### Validación obligatoria de éxito
- El guardado se ejecuta sin error.
- La UI retorna a pantalla principal.
- Se confirma persistencia del endpoint nuevo al reingresar a `OCPP Settings`.

### Regla crítica
- Nunca considerar aplicado un cambio sin `Save` + espera de impacto + verificación de persistencia.

---

## Bloque 2: Network Interfaces (IP estática)

### Objetivo
Definir conectividad de red del cargador en modo estático cuando se requiera operación controlada en laboratorio/cliente.

### Configuración típica aplicada
- Modo: de DHCP a IP estática
- Network mask: `255.255.255.0`
- Gateway: puerta de enlace de la subred objetivo
- DNS principal: `8.8.8.8`

### Pasos observados
1. Ir a `Network Interfaces`.
2. Cambiar de DHCP a configuración estática.
3. Cargar IP, máscara, gateway y DNS.
4. Ejecutar `Save`.
5. Esperar procesamiento y retorno a página principal (sale de setup).

### Validación obligatoria
- Save ejecutado.
- Retorno a principal completado.
- Reingreso a `Network Interfaces` y verificación de persistencia.

---

## Bloque 3: System Maintenance (logs de eventos)

### Objetivo
Descargar logs de eventos para análisis histórico y diagnóstico contextual del cargador.

### Reingreso esperado
- Si la UI expulsa de setup o del cargador, volver a autenticarse y reingresar.
- Es normal que el cargador tome un tiempo antes de permitir continuidad operativa.

### Fuentes de logs
- En `System Maintenance` aparecen logs de eventos y cambios.
- En algunos modelos se visualizan como `log OCPP` y `log HDME`.

### Uso analítico
- Permiten pasar de “foto instantánea” a histórico real de comportamiento.
- Base para análisis agregados de 7 o 15 días.
- Se usan para revisar intentos de carga, resultados, y errores.

### Paso crítico observado
1. Ingresar a `System Maintenance`.
2. Pinchar primero en el primer `log de eventos` (referente a comunicaciones del cargador).
3. Esperar a que finalice la descarga.

### Nota de rendimiento
- La descarga suele tardar: el proceso implica conexión al cargador y autorización para exportar.
- Demoras de 20–30 segundos (o más) pueden ser normales.
- Si queda en loop, verificar bloqueo del browser por descarga de ZIP desde sitio marcado como no seguro.
- Mitigación operativa: usar perfil de navegador dedicado para laboratorio con permisos de descarga habilitados para Saiwall.

---

## Bloque 3.1: Gestión de evidencia de logs (regla transversal Webasto/Unite)

### Regla general
- La descarga de logs puede variar en velocidad (desde segundos hasta 2–3 minutos o más).
- Esta lógica aplica a cualquier análisis Webasto/Unite (laboratorio o cliente), no solo Colonial.

### Artefactos críticos
- Descargar ambos logs de eventos (comunicaciones + cambios/HDMI).
- Estos logs son el corazón del análisis técnico del cargador.

### Control de evidencia
- Definir y mantener carpeta de trabajo por muestra/caso para conservar trazabilidad.
- Requisito: conocer siempre la ruta donde se descargan los ZIP.

---

## Bloque 4: Firmware + Reset (System Maintenance)

### Firmware
- Versión observable en el caso actual: `3.166`.
- La sección de firmware permite cargar archivo local y ejecutar actualización.

### Flujo de actualización observado
1. Entrar al menú de firmware.
2. `Upload`.
3. Seleccionar archivo local de firmware.
4. Ejecutar actualización (acción de ejecución posterior al upload).

### Notas de versiones
- Existen versiones anteriores (ej. series 1.x, 2.x) con menor estabilidad frente a releases más nuevos.

### Resets disponibles
1. `Hard reset`:
   - Reboot de unidad.
   - Corta comunicaciones del cargador durante el reinicio.
2. `Software reset`:
   - Reinicio lógico (más liviano).
3. `Factory reset` (en otro tab/menú):
   - Riesgo alto: puede limpiar configuración.
   - Puede dejar el cargador fuera del esquema previo de acceso/configuración.

### Uso operativo de reset
- `Software reset` y `Hard reset` se utilizan como etapas de reinicio para consolidar impacto de cambios.
- `Factory reset` no ejecutar sin decisión explícita por su impacto destructivo.

---

## Bloque 5: Backend CPMS (Plus / Eva / Wings)

### Contexto de plataformas
- Se operan tres variantes de backend OCPP para CPMS:
  1. Plus (local)
  2. Eva (local/red)
  3. Wings (cloud)

### Regla de endpoint (local)
- Puede resolverse por mDNS, por ejemplo:
  - `grid-code-1.local`
  - `grid-code-3.local`
- Cada hostname mDNS puede mapear a una IP subyacente en la red local.
- En el caso mostrado, se indicó mapeo operativo hacia IP de la instancia objetivo (ej. `...31.266` para el nodo mencionado).

### Acceso estándar del software
- Credencial base operativa indicada para esta demo: `admin / 1234`.

### Tabs prioritarios de trabajo
1. `Chargers`
2. `Metrics`
3. `Users` (cuando aplique)
4. `Serials`

### Alcance inmediato
- El siguiente aprendizaje se centra en la operativa sobre esos 4 tabs.

---

## Bloque 5.1: CPMS - Tab Chargers (alta y gestión de cargadores)

### Señales de contexto a verificar al entrar
1. Nombre de instancia/ecosistema.
2. IP mostrada en interfaz (debe coincidir con IP objetivo de operación).
3. Estado de conexión a `Nubas` (monitorización/inicialización): registrar conectado/no conectado.

### Alta de cargador (caso mostrado)
Objetivo: crear registro para que el backend reciba al cargador cuando apunte al endpoint.

Campos observados en el alta:
- `name` (etiqueta operativa, no crítica)
- `id` del cargador (crítica)
- `connector` (en este caso: 1 por ser unidad single connector)
- `phase/config` (caso mostrado: monofásico)
- `line` (caso mostrado: línea 3)
- `power_kw` (caso mostrado: 7.4 kW)
- `ocpp_version` (caso mostrado: OCPP 1.6)
- `priority` (caso mostrado: alta)

Caso demo indicado:
- Nombre de prueba (Laia)
- ID cargador: `142`
- Se crea el cargador para que el backend lo reciba cuando el equipo apunte al endpoint.

### Comportamiento esperado post-alta
- Estado visual pasa de no enlazado (marrón/anaranjado) a activo (verde) cuando enlaza correctamente.

### Selector crítico: esquema de autorización (choice triple)
Al editar/crear cargador, existe selector de quién autoriza la carga:
1. `Local CPMS` (instancia local):
   - La instancia local gestiona usuarios/autorizaciones.
   - Además de potencia, también gestiona autorización.
2. `Backend cloud`:
   - La instancia local opera como gateway/espejo.
   - Flujo: cargador pide autorización -> local reenvía -> backend responde (`accepted`/`rejected`) -> local devuelve al cargador.
   - Backend observa mismo ID por canal WebSocket espejado.
3. `Charger local` (mismo cargador):
   - El cargador decide autorizaciones según su configuración propia.
   - Ejemplos: `free charging` o validación RFID local.

### Regla de coherencia con WebUI del cargador
- Si en cargador `Free Charge Mode Active = true`, y el esquema es `Charger local`, el cargador puede autorizar por sí solo.
- Si se pretende control de autorización por backend, mantener `Free Charge Mode Active = false` y esquema `Backend cloud` (o local CPMS según arquitectura activa).

### Escenarios multi-connector
- Si la unidad es doble/múltiple:
  1. editar o crear entrada adicional, o
  2. usar función `clone` para replicar configuración.
- Ajustar número de conector según capacidad del equipo (referencia operativa indicada: hasta 10).
- Mantener coherencia de ID físico del cargador cuando aplique.

### Capacidades clave a cubrir en automatización
1. Crear uno o más cargadores.
2. Configurar esquema de autorización correcto.
3. Clonar para conectores múltiples.
4. Verificar transición de estado visual/operativo tras enlace.

---

## Bloque 5.2: CPMS - Tab Metrics

### Objetivo operativo
Usar métricas para diagnóstico rápido de estado, sesiones, autorizaciones y estabilidad de conexión por cargador.

### Métricas clave (Chargers)
1. Estado agregado de cargadores:
   - disponibles
   - no disponibles
   - preparing / charging / finishing (u otros estados visibles)
2. Sesiones:
   - activas en tiempo real
   - resumen/histórico de sesiones

### Autorizaciones (punto crítico)
- Revisar intentos de autorización y su resultado.
- Caso típico: RFID/tarjeta intenta autorizar y no está validada (rechazo).
- Utilidad:
  1. Identificar código enviado por cargador.
  2. Usar ese código subyacente para alta de nuevo usuario (flujo posterior en Users).

### Connection Monitoring (diagnóstico de estabilidad)
- Seleccionar cargador específico y revisar:
  - tiempo conectado
  - interrupciones/desconexiones
- Ejemplo observado: cargador sin caídas en el período consultado.

### Valor diagnóstico (local vs cloud)
- Permite desacoplar origen del problema:
  1. problema local (instancia/cargador)
  2. problema de conectividad o backend cloud
- Si se opera con backend remoto, también se inspeccionan caídas frente al backend para separar causa de falla.

### Capacidades a automatizar
1. Snapshot de estados agregados.
2. Extracción de intentos de autorización recientes.
3. Extracción de eventos de conexión/desconexión por cargador.
4. Clasificación preliminar: incidencia local vs incidencia cloud.

---

## Bloque 5.3: CPMS - Tab Users

### Modos de carga de usuarios
- Existen dos vías:
  1. importación masiva
  2. carga manual
- En esta fase se prioriza carga manual.

### Alta manual de usuario (caso mostrado)
Campos trabajados:
1. `name` / nombre completo
2. `username`
3. `password` (regla: mínimo/longitud operativa 6 dígitos)
4. `tag_id` (RFID para autorización en cargador)
5. `company`
6. `priority`
7. `role`

Caso demo:
- Nombre: Laia Botardo Gentile
- Username: laia
- Password demo: 123456
- Tag ID: valor de prueba (luego reemplazar por RFID real capturada)
- Prioridad: High

### Prioridades energéticas
- El sistema maneja 4 niveles escalares.
- Operación habitual: `High`.
- Lectura funcional:
  - alta prioridad => mayor peso sobre energía disponible
  - baja prioridad => asignación de cortesía/reducida

### Roles y alcance
Roles de administración/gestión (visión amplia de instancia):
- owner
- maintainer
- admin

Rol de operación de carga EV (alcance limitado):
- user
  - acceso a sus propios datos
  - acceso a cargadores habilitados de su instalación

### Regla operativa principal
- Si el objetivo es habilitar carga EV: crear rol `user` con tarjeta RFID asociada.
- Si el objetivo es demo/comercial del sistema completo: crear rol `owner` para habilitar tabs y capacidades totales de la plataforma (incluyendo gestión de otros usuarios).
- La selección de rol debe responder al objetivo operativo del alta.

### Resultado esperado post-alta
- Usuario queda activo en CPMS.
- Puede autenticarse en sistema local con `username/password` definidos.
- Puede autorizar carga por RFID cuando `tag_id` coincida con tarjeta real.

### Vínculo con tab Metrics
- `tag_id` real suele surgir del intento de autorización rechazado visto en Metrics.
- Flujo recomendado:
  1. detectar código RFID en Metrics
  2. crear/editar user con ese `tag_id`
  3. reintentar autorización y validar aceptación

---

## Bloque 5.4: CPMS - Settings / Configuraciones

### Sección General
Permite definir parámetros base de la instancia:
1. Nombre de la instancia
2. Dirección/ubicación
3. Tipo de red (trifásica/monofásica)
4. Unidad de visualización (amperios o kW)
5. Moneda (EUR, USD, etc.)
6. Nivel de customización visual (imagen)

### Sección Operacional
1. Operador principal (quién instaló/configuró instancia)
2. Estado de alertas habilitadas

### Sección Connections (crítica)
#### 1) Endpoint maestro para cargadores
- Es el endpoint que se configura en cargadores para que establezcan vínculo WebSocket con su servidor maestro.
- Punto crítico: debe estar alineado con la configuración OCPP del cargador.

#### 2) Dominio local / mDNS
- Define acceso rápido a la instancia por hostname local.

#### 3) Endpoints de telemetría energética
- Power meter endpoint (medición de red en tiempo real)
- Fotovoltaica endpoint (si aplica)

#### 4) Endpoint de autorización externa
- Permite espejar/rebotar autorizaciones hacia backend externo.
- Arquitectura objetivo descrita:
  - instancia local mantiene DLM/operación de potencia
  - backend externo gestiona autorizaciones/comunicaciones de acceso

### Regla de coherencia técnica
- Endpoint de cargador (WebUI OCPP) y endpoint maestro en CPMS deben ser consistentes.
- Si se usa autorización externa, validar que el selector de autorización en Chargers esté en modo compatible (`Backend cloud` o diseño definido) y que `Free Charge Mode Active` no contradiga el control de autorizaciones esperado.

### Submenú Energy (DLM operativo)
Define la lógica de reparto de energía y límites dinámicos de carga.

Parámetros clave:
1. Potencia de instalación y factor de potencia.
2. Presencia/estado de `power meter` instalado.
3. `Main Distribution Limit`:
   - límite del interruptor principal del edificio
   - normalmente asociado a medición principal.
4. `Circuit Distribution Limit`:
   - límite del cuadro eléctrico dedicado a cargadores.
5. `Operator Sub Distribution Limit`:
   - límite operativo real decidido por operación (aunque el cuadro permita más).
   - modela la realidad de cargadores efectivamente instalados/operables.

Lógica funcional esperada:
- El sistema calcula disponibilidad para EV teniendo en cuenta:
  1. capacidad del edificio,
  2. carga disponible para cargadores,
  3. reserva necesaria para el resto del edificio.

Límites globales por cargador:
- Se fija tope mínimo y máximo de corriente aplicable a todos los cargadores gestionados.
- Ejemplo operativo indicado:
  - mínimo: 6 A
  - máximo: 32 A

Prioridades de carga:
- `High`, `Medium`, `Low`, `Very Low`.
- Son configurables y aplicables tanto a usuarios como a cargadores.

### Capacidades a automatizar
1. Snapshot de configuración general/operacional.
2. Extracción y validación de endpoints críticos.
3. Snapshot y validación de parámetros DLM (Energy).
4. Chequeo de consistencia entre:
   - endpoint maestro CPMS
   - endpoint OCPP en cargadores
   - ruta de autorización (local vs backend externo)
5. Verificación de límites min/max globales y prioridades activas.

---

## Bloque 5.5: CPMS - Settings (System / Maintenance)

### Corrección de nomenclatura
- En este software la sección correcta es `Settings`.
- No corresponde tratarla como tab separado `Serials` para este flujo.

### User Manager local (crítico)
1. `User Manager` deshabilitado:
   - no hay autorizaciones en modo local.
2. `User Manager` habilitado:
   - el modo local puede autorizar usuarios/tarjetas.

### Maintenance / Identificación de instancia
Permite verificar:
1. Identidad de la instancia (código/ID)
2. Estado de módulos activos
3. Estado operativo general de componentes
4. Reinicio del sistema desde panel

### Regla operativa
- Antes de diagnosticar fallos de autorización local, validar primero estado de `User Manager`.
- Para auditoría técnica, registrar identificación de instancia + módulos activos.

---

## Estado de cobertura actual
- Bloques críticos de operación Webasto/Unite y CPMS documentados.
- Pendiente: empaquetado final en pipeline Python v2 (playwright + contrato + validaciones cruzadas).
