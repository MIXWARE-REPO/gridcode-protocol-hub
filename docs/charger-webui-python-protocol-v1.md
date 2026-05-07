# Protocolo Python estricto — Manipulación de cargador por Web UI (v1)

Objetivo: procedimiento único para conectarse al cargador, leer/cambiar endpoint OCPP, guardar cambios (botón Save), descargar logs OCPP y verificar evidencia.

## Inputs mínimos
- `ip` (ej. 192.168.31.138)
- `username`
- `password`
- `target_endpoint` (cuando aplique cambio)
- `output_zip_path` (ruta de descarga)

## Módulo Python
- `shared/orchestration/charger_webui_protocol_v1.py`

Funciones clave:
- `login_session(creds)`
- `get_current_ocpp_endpoint(session, ip)`
- `set_ocpp_endpoint_and_save(session, creds, target_endpoint)`
- `download_ocpp_logs_zip(session, ip, out_path)`

## Flujo obligatorio
1) Login con sesión autenticada.
2) Leer endpoint actual (`before_endpoint`).
3) Si hay cambio:
   - setear `centralSystemAddress = target_endpoint`
   - enviar `ocpp_button = Save`
   - re-leer endpoint (`after_endpoint`) y validar persistencia.
4) Descargar ZIP OCPP desde `downloadOcppLogs.php`.
5) Registrar evidencia:
   - before/target/after endpoint,
   - saved true/false,
   - nombre/tamaño del ZIP,
   - timestamp ejecución.

## Regla crítica del 05 de mayo (a fuego)
- Un cambio OCPP NO se considera aplicado hasta confirmar persistencia real por relectura post-guardado.
- No alcanza con “parece guardado” en pantalla.

## Modo Free
- Si en logs aparece `#freecharging` como idTag, interpretar “modo Free” (sin validación por identificación nominal de usuario).

## Resultado esperado
Salida operativa por cargador:
- endpoint actual,
- endpoint objetivo (si hubo cambio),
- estado de guardado real,
- archivo de logs descargado,
- base para análisis OCPP posterior.
