# CPMS WINGS — Alta de cargador AC monofásico (Playwright) v1

## Objetivo
Dejar el procedimiento totalmente estandarizado para que el script Python solo requiera cambiar credenciales y datos del cargador.

Caso validado en runtime:
- URL: `https://wings.grid-code.tech`
- alta exitosa de cargador ID `142`
- endpoint OCPP confirmado: `ws://wings.grid-code.tech:8080`

---

## 1) Parámetros de entrada (contractuales)
```json
{
  "base_url": "https://wings.grid-code.tech",
  "username": "admin",
  "password": "REEMPLAZAR",
  "charger": {
    "name": "AC-Monofasico-142",
    "id": "142",
    "type": "AC",
    "phase": "Single-Phase"
  }
}
```

Campos variables por ejecución:
- `username`
- `password`
- `charger.name`
- `charger.id`

Campos normalmente fijos para este caso:
- `charger.type = AC`
- `charger.phase = Single-Phase`

---

## 2) Flujo funcional
1. Ir a login de WINGS.
2. Ingresar credenciales y enviar.
3. Entrar a `MY CHARGERS`.
4. Click en `ADD CHARGER`.
5. Completar:
   - Name
   - ID
   - Type = AC
   - Phase = Single-Phase
6. Click en `Add`.
7. Validar mensaje de éxito: `It's all ok!`.
8. Cerrar modal.
9. Ir a `CONFIGURATIONS` → `CONNECTION SETTINGS`.
10. Leer OCPP URL y reportarla.

---

## 3) Selectores verificados (UI real)
### Login
- Usuario: `input[placeholder="Username"]` (fallback: `input[name="username"]`)
- Password: `input[placeholder="Password"]` (fallback: `input[name="password"]`)
- Submit: botón con texto `SUBMIT`

### Navegación
- Menú: link `MY CHARGERS`
- Botón: `ADD CHARGER`

### Modal alta cargador
- Name: textbox placeholder `E.g. Parking Nº1`
- ID: textbox placeholder `E.g. P01`
- Tipo: combobox valor por defecto `AC`
- Fase: combobox valor `Single-Phase`
- Acción: botón `Add`
- Confirmación: texto `It's all ok!`

### Endpoint OCPP
- Menú: `CONFIGURATIONS`
- Tab: `CONNECTION SETTINGS`
- Sección: `OCPP URL`
- Valor observado: `ws://wings.grid-code.tech:8080`

---

## 4) Reglas de robustez para el Python
1. Espera explícita post-login (2–3 s) y validar presencia de `MY CHARGERS`.
2. Siempre validar apertura del modal `ADD CHARGER` antes de escribir.
3. Si `Type` no es `AC`, forzar selección.
4. Si `Phase` no es `Single-Phase`, forzar selección.
5. Confirmar éxito por texto (`It's all ok!`) o toast equivalente.
6. Si no hay confirmación, devolver error contractual y screenshot.
7. En endpoint OCPP, no hardcodear: leer del bloque `OCPP URL` y devolverlo en output.

---

## 5) Estructura de salida recomendada
```json
{
  "status": "ok",
  "login": "ok",
  "charger_create": {
    "name": "AC-Monofasico-142",
    "id": "142",
    "result": "ok",
    "success_message_seen": true
  },
  "ocpp": {
    "url": "ws://wings.grid-code.tech:8080",
    "source": "CONFIGURATIONS/CONNECTION SETTINGS/OCPP URL"
  },
  "evidence": {
    "screenshots": [],
    "html": []
  }
}
```

---

## 6) Checklist final (pre-producción)
- [ ] Login válido con credenciales actuales.
- [ ] Apertura de `MY CHARGERS` estable.
- [ ] `ADD CHARGER` abre modal correctamente.
- [ ] Alta de cargador confirma `It's all ok!`.
- [ ] OCPP URL leído desde UI y retornado en output.
- [ ] Evidencia guardada (capturas + html).

---

## 7) Nota operativa
Para este flujo, el desarrollo Python queda reusable cambiando solo:
- credenciales
- nombre/id del cargador

Mantener selectores con fallback y validación de salida contractual para evitar desvíos.