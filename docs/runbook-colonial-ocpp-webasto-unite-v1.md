# Runbook limpio y estructurado — Colonial/Webasto UNITE (OCPP)

Objetivo: dejar un camino único, repetible y registrable para operar cargadores por IP fija, ajustar endpoint OCPP y analizar logs.

## Evidencia documental consolidada (fuente)
Este runbook se consolida desde las skills operativas que ya contienen los hallazgos:
- `colonial-charger-analysis-execution`
- `ocpp-log-unpack-7d-analysis`
- `gridcode-aggregated-behavior-remote-analysis`
- `colonial-vpn-charger-access`

Hallazgos heredados clave ya validados en documentación:
- UI: `UNITE Configuration Interface`.
- Campo crítico OCPP: `Central System Address`.
- Botón de guardado: `id="ocpp_button"` (texto `Save`, `onclick="checkOcppForm()"`).
- Descarga de logs OCPP: `downloadOcppLogs.php`.
- Trigger de botón logs: `id="ocpp_log_button"` con `onclick="location.href='downloadOcppLogs.php'"`.
- Caso observado: el browser remoto puede timeout al abrir `downloadOcppLogs.php`, pero la descarga puede completarse en segundo plano.

## Flujo maestro (estricto)

### Fase A — Acceso y lectura base
1. Abrir `http://<IP_CARGADOR>/`.
2. Login con usuario/clave vigentes.
3. Confirmar sesión activa (menú y datos visibles).
4. Registrar:
   - timestamp inicio,
   - IP,
   - usuario,
   - firmware/UI visible.

### Fase B — Endpoint OCPP (set + verificación)
1. Ir a `OCPP Settings`.
2. Leer y guardar `before_endpoint`.
3. Escribir endpoint objetivo en `Central System Address`.
4. Guardar con `Save` (`#ocpp_button`).
5. Verificación obligatoria:
   - salir y reingresar a `OCPP Settings`,
   - leer `after_endpoint`.
6. Éxito solo si `after_endpoint == endpoint_objetivo`.

Regla crítica:
- Si no se puede confirmar persistencia tras recarga, el cambio NO se considera aplicado.

### Fase C — Descarga de logs OCPP
1. Ir a `System Maintenance` (si abre en UI).
2. Disparar descarga OCPP por botón (`ocpp_log_button`) o por endpoint `downloadOcppLogs.php` con sesión autenticada.
3. Si browser remoto entra en timeout, validar por artefacto descargado en disco/historial.
4. Registrar evidencia:
   - nombre archivo,
   - tamaño,
   - hash (si aplica),
   - ruta final.

### Fase D — Análisis 7 días
1. Ejecutar `ocpp-log-unpack-7d-analysis` sobre ZIP descargado.
2. Extraer métricas:
   - sesiones totales/exitosas,
   - fallos inicio,
   - interrupciones,
   - reinicios,
   - patrón horario.
3. Clasificar criticidad:
   - >70 sano,
   - 50–70 seguimiento,
   - 40–50 alta,
   - <40 máxima.

### Fase E — Decisión y reporte
1. Si resolución remota viable: cerrar remoto con evidencia.
2. Si no viable o criticidad alta/máxima: escalar onsite.
3. Emitir reporte remoto con plantilla fija aprobada (sin rediseño).

## Registro mínimo por ejecución
- `ticket_id`
- `charger_id` / IP
- `before_endpoint`
- `target_endpoint`
- `after_endpoint`
- resultado de guardado (OK/FAIL)
- log descargado (sí/no, nombre, tamaño)
- criticidad
- decisión final (remoto/onsite)

## Anti-desvío (obligatorio)
- Prohibido cerrar caso sin verificar persistencia real del endpoint.
- Prohibido declarar fallo de logs solo por timeout visual del navegador.
- Prohibido alterar estética/estructura de plantillas de reporte aprobadas.

## Salida humana esperada
Resumen ejecutivo por cargador:
- a dónde estaba apuntando,
- si el cambio quedó aplicado,
- fecha/hora de actividad de cargas en ventana analizada,
- si las cargas fueron correctas,
- decisión: remoto resuelto o escalar onsite.
