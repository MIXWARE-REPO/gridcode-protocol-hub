# Auditoría y robustecimiento de skills — diagnóstico inicial

## Objetivo
Canonizar los avances ya hechos, eliminar duplicidades y dejar una arquitectura de skills más clara, robusta y mantenible.

## 1) Estado actual — diagnóstico inicial

### A. Capa ya bastante madura
Hay varias skills que ya apuntan a un nivel productivo real:
- `ticket-handler` para soporte GC-EV.
- `gestion-de-mails-laia` y su rail de estilo para correo operativo.
- `pdf-builder` y `gridcodear-documentos` para documentos corporativos.
- `webasto-*`, `cpms-*` y `nuba-*` como familias con ejecución operativa real.
- `calendar-meet-host-gridcode` y varias skills de productividad/agenda.

### B. Capa intermedia todavía heterogénea
Hay familias con intención clara pero con solapamientos o variantes que aún compiten entre sí:
- análisis remoto Webasto/Unite (`gridcode-aggregated-behavior-remote-analysis` vs `webasto-unite-log-analysis-production-report`)
- rails de email internos/externos
- familias GitHub / Google Workspace / Meet / Drive con varias piezas que podrían quedar mejor jerarquizadas

### C. Capa de catálogo/canonización incompleta
El catálogo real ya existe, pero todavía necesita:
- clasificación estricta por capa: frontend / service / backend
- una sola skill canónica por intención de usuario
- democión explícita de helpers y alias
- mantenimiento de mapas y docs sincronizados

## 2) Gaps y vulnerabilidades detectadas

### 2.1 Duplicidad funcional
Hay skills distintas que cubren la misma intención o casi la misma intención.
Riesgo:
- el usuario puede llegar a rutas distintas para la misma tarea
- la automatización puede escoger la skill incorrecta
- aumenta la deuda operativa y el coste de mantenimiento

### 2.2 Frontera poco clara entre frontend, service y backend
Algunas skills son verdaderos frontends; otras son helpers o backend plumbing pero están expuestas como si fueran capacidades de usuario.
Riesgo:
- catálogo ruidoso
- rutas públicas sobredimensionadas
- mezcla de intención del usuario con implementación interna

### 2.3 Contratos no uniformes
No todas las skills dejan igual de claro:
- input contract
- output esperado
- límites de uso
- validación post-ejecución
- evidencia mínima

Riesgo:
- resultados menos predecibles
- más error humano o de routing

### 2.4 Falta de canonización documental
Hay avances hechos, pero no todos están reflejados de forma uniforme en:
- skill metadata
- mapas de frontends/services/backends
- docs de referencia
- reglas de decisión para futuras altas

Riesgo:
- drift entre código, docs y operación

### 2.5 Exceso de crecimiento horizontal
El catálogo está creciendo por familias nuevas y variantes.
Riesgo:
- dificultad para encontrar la skill correcta
- mayor probabilidad de solapamientos futuros
- mantenimiento más lento

## 3) Propuesta de plan estructurado de mejora

### Fase 0 — Inventario y canonización
Objetivo: tener una foto real del estado actual.

Entregables:
- inventario completo de skills
- clasificación por capa
- listado de duplicadas / variantes / helpers / pendientes
- mapa de familias canónicas

### Fase 1 — Auditoría de colisiones
Objetivo: revisar una por una las zonas solapadas.

Prioridad sugerida:
1. Email
2. PDF / documentos
3. Webasto / Unite / CPMS / NUBA
4. Google Workspace / Meet / Drive
5. GitHub / gestión operativa
6. Social / misc

Entregables:
- collision matrix
- decisiones de merge / alias / helper / deprecate
- lista de skills supervivientes

### Fase 2 — Robustecimiento de contratos
Objetivo: hacer cada skill más predecible.

Acciones:
- definir input/output contract en todas las skills relevantes
- añadir validación de error homogénea
- documentar comportamiento esperado y fallback
- estandarizar evidencia y artefactos

### Fase 3 — Taxonomía y capas
Objetivo: separar claramente lo que ve el usuario de lo que es infraestructura interna.

Regla objetivo:
- Frontend: lo que el usuario pide directamente
- Service: apoyo reusable que no debería ser entrada principal
- Backend: plumbing, autenticación, transporte, persistencia, scheduling, adaptadores

Entregables:
- mapa limpio de capas
- catálogo público reducido
- helpers internos explícitos

### Fase 4 — Pruebas y validación
Objetivo: que cada skill importante tenga una prueba real o un runner determinista.

Acciones:
- pruebas unitarias donde aplique
- runners productivos contractuales
- validación post-run
- checks de regresión para rutas críticas

### Fase 5 — Gobernanza continua
Objetivo: evitar que el catálogo vuelva a degradarse.

Acciones:
- regla de alta nueva: primero comprobar si existe skill canónica
- toda skill nueva debe declararse frontend/service/backend
- toda variante debe justificar por qué no es alias
- revisión periódica de duplicidades

## 4) Criterios de canonización
Una skill debe quedarse como canónica si:
- resuelve una intención real de usuario
- tiene contrato claro
- tiene salida predecible
- está validada end-to-end
- no compite con otra skill equivalente

Si dos skills cubren lo mismo:
- una queda como canónica
- la otra se convierte en helper, alias o se depreca

## 5) Riesgos principales del plan
- tocar demasiado catálogo sin primero fijar taxonomía
- eliminar helpers útiles por parecer duplicados
- mantener variantes por comodidad histórica
- no sincronizar docs y metadata al mismo tiempo

## 6) Resultado esperado
Un catálogo más pequeño, más claro y más fiable:
- una intención = una ruta canónica
- helpers internos ocultos o demotados
- contratos más estrictos
- menos ambigüedad en routing
- mayor facilidad para mantener y escalar el sistema
