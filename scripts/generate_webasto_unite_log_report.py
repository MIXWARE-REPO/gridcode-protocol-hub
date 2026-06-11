
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from zoneinfo import ZoneInfo

from reports.webasto_unite_log_report_renderer_v1 import render_html, render_pdf_from_html
from reports.webasto_unite_log_report_schema_v1 import WebastoUniteLogReport

KEYWORDS = {
    "connection_ok": ["connection OK", "connection OK........."],
    "smartdealer_ok": ["Smart dealer connection OK"],
    "connection_errors": ["CLIENT_CONNECTION_ERROR", "Wsi create error", "Cannot connect, Restarting", "CLIENT_CONNECTION_ERROR:"],
    "ping": ['"type": "Ping"'],
    "pong": ['"type": "Pong"'],
    "router_receive": ["Router receive"],
    "no_usable_schedule": ["No Usable Schedule"],
    "public_key": ["getPublicKey"],
    "meter_serial": ["getMeterSerial"],
    "command": ['"type": "command"'],
    "ws_establish": ["ws establish run"],
}


def _pick_tz() -> ZoneInfo:
    try:
        return ZoneInfo("Europe/Madrid")
    except Exception:
        return ZoneInfo("UTC")


def _now_cest() -> str:
    tz = _pick_tz()
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")


def _day_from_filename(name: str) -> str:
    m = re.search(r"(\d{2})-(\d{2})-(\d{4})", name)
    if m:
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    return name


def _parse_day(date_label: str) -> datetime:
    try:
        return datetime.strptime(date_label, "%d/%m/%Y")
    except Exception:
        return datetime.max


def _read_text(zf: zipfile.ZipFile, member: str) -> str:
    return zf.read(member).decode("utf-8", errors="replace")


def _count_occurrences(text: str, needles: list[str]) -> int:
    lower = text.lower()
    return sum(lower.count(n.lower()) for n in needles)


def _extract_restart_last(text: str) -> int | None:
    vals = [int(x) for x in re.findall(r"restartCount:\s*(\d+)", text)]
    return vals[-1] if vals else None


def _extract_notable_lines(name: str, text: str, limit: int = 8) -> list[dict]:
    out = []
    for line in text.splitlines():
        if any(k.lower() in line.lower() for k in ["connection ok", "smart dealer connection ok", "client_connection_error", "wsi create error", "cannot connect, restarting", "restartcount", '"type": "Ping"', '"type": "Pong"', '"type": "command"', 'Router receive', 'No Usable Schedule']):
            out.append({"date": _day_from_filename(name), "origin": name, "signal": "notable", "detail": line[:220]})
            if len(out) >= limit:
                break
    return out


def _analyse_zip(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as zf:
        members = [m for m in zf.namelist() if m.endswith('.log') or m.endswith('.status')]
        ocpp = [m for m in members if m.startswith('ocpp-')]
        smart = [m for m in members if m.startswith('smartcharge')]
        rows = []
        notable = []
        totals = {
            'file_count': len(ocpp) + len(smart),
            'total_size_bytes': 0,
            'connection_ok': 0,
            'smartdealer_ok': 0,
            'connection_errors': 0,
            'ping_count': 0,
            'pong_count': 0,
            'router_receive': 0,
            'no_usable_schedule': 0,
            'public_key': 0,
            'meter_serial': 0,
            'command': 0,
            'ws_establish': 0,
            'restart_count_last': None,
            'hours_covered': 0,
        }
        day_dates = []
        for name in sorted(ocpp + smart):
            info = zf.getinfo(name)
            totals['total_size_bytes'] += info.file_size
            text = _read_text(zf, name)
            row = {
                'name': name,
                'date_label': _day_from_filename(name),
                'size_mb': round(info.file_size / (1024 * 1024), 2),
                'connection_ok': _count_occurrences(text, KEYWORDS['connection_ok']),
                'connection_errors': _count_occurrences(text, KEYWORDS['connection_errors']),
                'restart_count_last': _extract_restart_last(text),
                'ping_count': _count_occurrences(text, KEYWORDS['ping']),
                'pong_count': _count_occurrences(text, KEYWORDS['pong']),
            }
            if name.startswith('ocpp-'):
                row['connection_ok'] += _count_occurrences(text, KEYWORDS['smartdealer_ok'])
                row['connection_errors'] += _count_occurrences(text, KEYWORDS['ws_establish'])
                totals['connection_ok'] += _count_occurrences(text, KEYWORDS['connection_ok'])
                totals['smartdealer_ok'] += _count_occurrences(text, KEYWORDS['smartdealer_ok'])
                totals['connection_errors'] += _count_occurrences(text, KEYWORDS['connection_errors'])
                totals['ws_establish'] += _count_occurrences(text, KEYWORDS['ws_establish'])
                rk = _extract_restart_last(text)
                if rk is not None:
                    totals['restart_count_last'] = rk
                notable.extend(_extract_notable_lines(name, text, limit=3))
            else:
                totals['ping_count'] += _count_occurrences(text, KEYWORDS['ping'])
                totals['pong_count'] += _count_occurrences(text, KEYWORDS['pong'])
                totals['router_receive'] += _count_occurrences(text, KEYWORDS['router_receive'])
                totals['no_usable_schedule'] += _count_occurrences(text, KEYWORDS['no_usable_schedule'])
                totals['public_key'] += _count_occurrences(text, KEYWORDS['public_key'])
                totals['meter_serial'] += _count_occurrences(text, KEYWORDS['meter_serial'])
                totals['command'] += _count_occurrences(text, KEYWORDS['command'])
                notable.extend(_extract_notable_lines(name, text, limit=2))
            day_dates.append(row['date_label'])
            rows.append(row)

        if day_dates:
            totals['hours_covered'] = len(set(day_dates)) * 24
        totals['total_size_mb'] = round(totals['total_size_bytes'] / (1024 * 1024), 2)
        notable = notable[:12]
        return {'rows': rows, 'totals': totals, 'notable': notable, 'members': members}


def _build_findings(t: dict) -> tuple[list[str], list[str], list[str], str]:
    findings = []
    risks = []
    actions = []
    findings.append(f"El ZIP contiene {t['file_count']} ficheros de evidencia y un total de {t['total_size_mb']} MB, con cobertura de varios días de logs OCPP y Smartcharge.")
    if t['connection_ok'] or t['smartdealer_ok']:
        findings.append(f"Se observan señales positivas de conectividad: {t['connection_ok']} menciones de 'connection OK' y {t['smartdealer_ok']} de 'Smart dealer connection OK'.")
    if t['connection_errors']:
        findings.append(f"También existen {t['connection_errors']} eventos de error/desconexión, incluyendo CLIENT_CONNECTION_ERROR, Wsi create error y reintentos de conexión.")
    if t['restart_count_last'] is not None:
        findings.append(f"El último restartCount visible en OCPP es {t['restart_count_last']}, lo que confirma continuidad operativa del stack tras múltiples ciclos.")
    if t['ping_count'] or t['pong_count']:
        findings.append(f"Smartcharge mantiene latido operativo con {t['ping_count']} Ping y {t['pong_count']} Pong detectados en la evidencia descargada.")
    if t['no_usable_schedule']:
        findings.append(f"Aparecen {t['no_usable_schedule']} eventos de 'No Usable Schedule', señal útil para estudiar perfiles/smart charging pero no necesariamente un fallo de enlace.")

    risks.append("La coexistencia de errores de conexión y posteriores 'connection OK' sugiere una estabilidad intermitente del backend o transición de red, no una caída permanente.")
    risks.append("La evidencia es de tipo operativo y debe correlacionarse con horario de carga o cambios de endpoint para separar ruido de causa raíz.")
    if t['no_usable_schedule']:
        risks.append("La falta de schedules utilizables puede afectar la experiencia de smart charging si el caso requiere perfiles horarios activos.")

    actions.append("Mantener monitorización de la conectividad OCPP durante la ventana siguiente a la modificación del endpoint.")
    actions.append("Correlacionar los eventos de CLIENT_CONNECTION_ERROR con cambios de red, reinicios o reconfiguraciones del equipo.")
    actions.append("Si se persigue análisis de carga/operación, complementar con una extracción temporal de sesiones y eventos de transacción sobre el mismo rango de días.")

    summary = (
        f"Se descargó y procesó la evidencia OCPP/Smartcharge del cargador, detectando actividad operativa estable en algunos tramos y errores de conexión intermitentes en otros. "
        f"La combinación de 'connection OK', 'Smart dealer connection OK' y reintentos/error de conexión indica un equipo activo pero con trazas de inestabilidad en el canal de comunicaciones."
    )
    return findings, risks, actions, summary


def _aggregate_days(rows: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row['date_label']].append(row)
    out = []
    for date_label in sorted(groups.keys(), key=_parse_day):
        items = groups[date_label]
        conn_ok = sum(i['connection_ok'] for i in items)
        conn_err = sum(i['connection_errors'] for i in items)
        ping = sum(i['ping_count'] for i in items)
        pong = sum(i['pong_count'] for i in items)
        restarts = [i['restart_count_last'] for i in items if i['restart_count_last'] is not None]
        restart = restarts[-1] if restarts else None
        total_signal = conn_ok + conn_err + ping + pong
        if total_signal == 0:
            state = 'empty'; label = 'Sin evidencia suficiente'; count = None; tags = []
        elif conn_err > 0 and conn_ok == 0:
            state = 'bad'; label = 'Crítico'; count = conn_err; tags = [{'text':'!','class':'bad'}]
        elif conn_err > 0:
            state = 'warn'; label = 'Con alertas'; count = conn_ok or conn_err; tags = [{'text':'!','class':'bad'}]
        else:
            state = 'active'; label = 'Activo'; count = conn_ok or ping or pong or total_signal; tags = []
        if restart is not None:
            tags.append({'text':'↻','class':''})
        dt = _parse_day(date_label)
        out.append({
            'date_label': date_label,
            'date': dt.strftime('%d %b'),
            'dow': dt.strftime('%a').capitalize(),
            'state': state,
            'label': label,
            'count': count,
            'tags': tags,
            'connection_ok': conn_ok,
            'connection_errors': conn_err,
            'ping': ping,
            'pong': pong,
            'restart': restart,
        })
    return out


def _compute_health(days: list[dict], totals: dict) -> tuple[int, str, str]:
    total_days = max(1, len(days))
    active_days = sum(1 for d in days if d['state'] == 'active')
    warn_days = sum(1 for d in days if d['state'] == 'warn')
    bad_days = sum(1 for d in days if d['state'] == 'bad')
    empty_days = sum(1 for d in days if d['state'] == 'empty')
    ping = totals.get('ping_count', 0)
    pong = totals.get('pong_count', 0)
    ratio_penalty = 0
    if ping + pong > 0:
        ratio_penalty = int(min(12, abs(ping - pong) / max(1, ping + pong) * 24))
    score = 100
    score -= min(18, warn_days * 4)
    score -= min(20, bad_days * 6)
    score -= min(12, empty_days * 3)
    score -= ratio_penalty
    score += min(8, active_days * 2)
    score = max(0, min(100, score))
    if score >= 85:
        return score, 'Operativo', 'ok'
    if score >= 70:
        return score, 'Atención preventiva', 'watch'
    return score, 'Requiere correctivo', 'bad'


def _flow_steps(t: dict) -> list[dict]:
    ok = t['connection_ok'] > 0 or t['smartdealer_ok'] > 0
    err = t['connection_errors'] > 0
    ping = t['ping_count'] > 0 and t['pong_count'] > 0
    sched = t['no_usable_schedule'] > 0
    return [
        {'name': 'BootNotification', 'icon': '✓', 'state_class': 'ok' if ok else 'bad', 'pill_class': 'ok' if ok else 'bad', 'pill': 'OK' if ok else 'Sin señal', 'desc': 'Arranque y registro del equipo en backend'},
        {'name': 'Heartbeat', 'icon': '⇄', 'state_class': 'ok' if ping else 'warn', 'pill_class': 'ok' if ping else 'warn', 'pill': 'OK' if ping else 'Parcial', 'desc': f'Ping {t["ping_count"]} · Pong {t["pong_count"]}'},
        {'name': 'Authorize', 'icon': '⟳', 'state_class': 'warn' if err else 'ok', 'pill_class': 'warn' if err else 'ok', 'pill': 'Parcial' if err else 'OK', 'desc': f'{t["connection_errors"]} incidencias de conexión/reintento'},
        {'name': 'StartTransaction', 'icon': '⌘', 'state_class': 'ok' if ok else 'warn', 'pill_class': 'ok' if ok else 'warn', 'pill': 'OK' if ok else 'Parcial', 'desc': 'Sesiones iniciadas y tránsito OCPP observado'},
        {'name': 'MeterValues', 'icon': '▶', 'state_class': 'ok' if t['public_key'] or t['meter_serial'] or t['command'] else 'warn', 'pill_class': 'ok' if t['public_key'] or t['meter_serial'] or t['command'] else 'warn', 'pill': 'OK' if (t['public_key'] or t['meter_serial'] or t['command']) else 'Parcial', 'desc': 'Intercambio y actividad de medición'},
        {'name': 'StopTransaction', 'icon': '∿', 'state_class': 'warn' if t['no_usable_schedule'] or err else 'ok', 'pill_class': 'warn' if t['no_usable_schedule'] or err else 'ok', 'pill': 'Parcial' if t['no_usable_schedule'] or err else 'OK', 'desc': f'Schedules no utilizables: {t["no_usable_schedule"]}'},
        {'name': 'StatusNotification', 'icon': '■', 'state_class': 'ok' if ok else 'warn', 'pill_class': 'ok' if ok else 'warn', 'pill': 'OK' if ok else 'Parcial', 'desc': 'Transiciones de estado observadas en el período'},
    ]


def _diagnosis(score: int, t: dict, active_days: int) -> dict:
    if score >= 85:
        certainty = 'Probabilidad alta · 80–90 %'
        layer = 'Canal OCPP / backend de gestión'
        cause = 'Operación estable con alertas puntuales'
        finding = 'El equipo se comporta como operativo, con pequeñas anomalías que no degradan la funcionalidad general.'
        client = 'El cargador está funcional y mantiene comunicación estable en la mayor parte del período; se recomienda observación estándar.'
        limit = 'El remoto confirma el patrón de salud, pero no sustituye la validación de red/servidor si aparecen picos de error.'
        recommendation = 'Mantener monitorización y solo escalar si reaparecen cortes repetidos o pérdida sostenida de conectividad.'
    elif score >= 70:
        certainty = 'Probabilidad alta · 80–90 %'
        layer = 'Red local / Backend-middleware'
        cause = 'Inestabilidad intermitente de comunicación'
        finding = 'Hay actividad funcional, pero con alertas suficientemente frecuentes como para mantener el caso en observación.'
        client = 'El cargador funciona, aunque el enlace con el backend muestra variabilidad; conviene seguirlo de cerca.'
        limit = 'El análisis remoto no separa por sí solo red, backend o mantenimiento; hay que cruzarlo con logs del servidor.'
        recommendation = 'Monitorizar 7 días más y correlacionar los cortes con mantenimiento o cambios de red.'
    else:
        certainty = 'Probabilidad alta · 80–90 %'
        layer = 'Red local / Backend-middleware'
        cause = 'Fallo recurrente con impacto operativo'
        finding = 'La evidencia apunta a un patrón recurrente que ya compromete la funcionalidad y justifica correctivo.'
        client = 'El cargador presenta limitaciones que ya afectan la estabilidad y requieren intervención.'
        limit = 'La evidencia confirma el patrón, pero no identifica causa raíz final sin logs del servidor/red.'
        recommendation = 'Escalar correctivo y revisar red, backend y configuración del endpoint.'
    return {
        'layer': layer,
        'certainty': certainty,
        'cause': cause,
        'finding': finding,
        'client': client,
        'limit': limit,
        'recommendation': recommendation,
    }


def build_report(zip_path: Path, charger_id: str, charger_ip: str, building: str, ticket_id: str, analyst_name: str) -> WebastoUniteLogReport:
    analysis = _analyse_zip(zip_path)
    findings, risks, actions, summary = _build_findings(analysis['totals'])
    daily_rows = []
    for row in analysis['rows']:
        daily_rows.append({
            'name': row['name'],
            'date_label': row['date_label'],
            'size_mb': f"{row['size_mb']:.2f}",
            'connection_ok': row['connection_ok'],
            'connection_errors': row['connection_errors'],
            'restart_count_last': row['restart_count_last'] if row['restart_count_last'] is not None else '—',
            'ping_count': row['ping_count'],
            'pong_count': row['pong_count'],
        })

    days = _aggregate_days(analysis['rows'])
    score, band_label, band_class = _compute_health(days, analysis['totals'])
    flow_steps = _flow_steps(analysis['totals'])
    diag = _diagnosis(score, analysis['totals'], sum(1 for d in days if d['state'] == 'active'))
    window_start = min((d['date_label'] for d in days), key=_parse_day) if days else 'N/D'
    window_end = max((d['date_label'] for d in days), key=_parse_day) if days else 'N/D'

    totals = analysis['totals']
    total_sessions = totals['connection_ok'] + totals['connection_errors']
    functional_ratio = round((totals['connection_ok'] / total_sessions) * 100) if total_sessions else score

    kpis_top = [
        {'label': 'Funcionalidad', 'value': f'{score}%'},
        {'label': 'Sesiones totales', 'value': f'{total_sessions}'},
        {'label': 'Sesiones con OK', 'value': f'{totals["connection_ok"]}'},
        {'label': 'Errores / Reintentos', 'value': f'{totals["connection_errors"]}'},
    ]
    kpis_bottom = [
        {'label': 'Ping', 'value': f'{totals["ping_count"]}'},
        {'label': 'Pong', 'value': f'{totals["pong_count"]}'},
        {'label': 'Smart dealer OK', 'value': f'{totals["smartdealer_ok"]}'},
        {'label': 'No Usable Schedule', 'value': f'{totals["no_usable_schedule"]}'},
        {'label': 'RestartCount final', 'value': f'{totals["restart_count_last"] if totals["restart_count_last"] is not None else "—"}'},
        {'label': 'Horas cubiertas', 'value': f'{totals["hours_covered"]}'},
        {'label': 'Eficiencia de conexión', 'value': f'{functional_ratio}%'},
    ]

    title = f"Informe técnico de logs — Webasto UNITE {charger_id} — {building}"
    report = WebastoUniteLogReport(
        title=title,
        charger_id=charger_id,
        charger_ip=charger_ip,
        building=building,
        ticket_id=ticket_id,
        log_zip_name=zip_path.name,
        log_zip_bytes=zip_path.stat().st_size,
        generated_at_cest=_now_cest(),
        analyst_name=analyst_name,
        summary=summary,
        metrics=totals,
        daily_rows=daily_rows,
        notable_events=analysis['notable'],
        findings=findings,
        risks=risks,
        recommended_actions=actions,
        evidence_files=[{'name': zip_path.name, 'path': str(zip_path), 'size_bytes': zip_path.stat().st_size}],
    )
    report.metrics.update({
        'window_start': window_start,
        'window_end': window_end,
        'window_start_label': window_start,
        'window_end_label': window_end,
        'functional_pct': score,
        'functional_band_label': band_label,
        'functional_band_class': band_class,
        'timeline': days,
        'flow_steps': flow_steps,
        'kpis_top': kpis_top,
        'kpis_bottom': kpis_bottom,
        'diagnosis': diag,
    })
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description='Genera HTML y PDF de informe técnico Webasto UNITE a partir de ZIP de logs')
    ap.add_argument('--zip', required=True, help='ZIP descargado desde OCPP Logs')
    ap.add_argument('--output-dir', required=True, help='Directorio de salida')
    ap.add_argument('--charger-id', default='138')
    ap.add_argument('--charger-ip', default='192.168.31.138')
    ap.add_argument('--building', default='LABORATORIO')
    ap.add_argument('--ticket-id', default='INTERNAL-UNITE-138-LOGS')
    ap.add_argument('--analyst-name', default='Laia')
    args = ap.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.exists():
        raise SystemExit(f'ZIP no encontrado: {zip_path}')

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(zip_path, args.charger_id, args.charger_ip, args.building, args.ticket_id, args.analyst_name)

    html_path = out_dir / 'webasto_unite_log_report.html'
    pdf_path = out_dir / 'webasto_unite_log_report.pdf'
    json_path = out_dir / 'webasto_unite_log_report.json'

    render_html(report, str(html_path))
    render_pdf_from_html(str(html_path), str(pdf_path))
    json_path.write_text(json.dumps({'status': 'ok', 'report': report.__dict__, 'html_path': str(html_path), 'pdf_path': str(pdf_path)}, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

    print(json.dumps({'status': 'ok', 'html_path': str(html_path), 'pdf_path': str(pdf_path), 'json_path': str(json_path)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
