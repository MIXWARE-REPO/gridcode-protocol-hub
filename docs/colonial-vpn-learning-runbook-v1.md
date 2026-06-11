# Colonial VPN — Runbook de aprendizaje asistido (AnyDesk + Browser)

Objetivo: garantizar una sesión fluida para demostrar un proceso y convertirlo en automatización Python determinista.

## 1) Pre-flight del entorno (antes de la demo)

Checklist obligatorio:
- Sesión gráfica activa en `DISPLAY=:0`.
- Browser visible por AnyDesk.
- OpenVPN instalado en Linux.
- URL de Saiwall accesible.

Comandos de verificación:
- `nmcli --version`
- `/usr/sbin/openvpn --version`
- `curl -I --max-time 20 https://colonial.saiwall.net:1192/vpnusers/login`

## 2) Arranque estable del browser para AnyDesk

Problema típico: el browser se abre en sesión no visible o queda inmanejable en fullscreen.

Secuencia estable:
1. Cerrar instancias previas:
   - `pkill -f '/usr/bin/google-chrome' || true`
2. Abrir en sesión gráfica correcta:
   - `DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus XAUTHORITY=/run/user/1000/gdm/Xauthority /usr/bin/google-chrome --new-window --start-maximized --incognito --no-first-run --no-default-browser-check <URL>`
3. Si queda en fullscreen:
   - enviar `F11` y `Escape` con `xdotool`.

Fallback recomendado:
- Si Chrome muestra errores de carga repetitivos (“Something has gone wrong”), abrir Firefox con misma URL y continuar demo.

## 3) Protocolo de sesión de aprendizaje

1. Operador humano ejecuta flujo completo una vez.
2. Se etiqueta cada paso con intención (“guardar”, “verificar persistencia”, “descargar eventos”).
3. Se capturan variables:
   - URL/base
   - usuario
   - MFA
   - endpoint objetivo
   - textos esperados de éxito/error
4. Se capturan validaciones obligatorias:
   - guardado confirmado
   - persistencia tras recarga
   - evidencia visual

## 4) Conversión a Python determinista

Salida mínima obligatoria:
- Script Playwright productivo.
- Input JSON contractual.
- Output JSON contractual.
- Errores normalizados (`error_code`).
- Evidencia (`screenshots`, `trace`, URL final, tiempos por paso).

## 5) Criterio de “listo para producción”

- Misma entrada => misma salida funcional.
- Reintentos y timeouts definidos.
- Paso de persistencia obligatorio en operaciones de configuración.
- Golden run aprobado por negocio.
