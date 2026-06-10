from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Dict, List, Sequence
from urllib.parse import quote

INTERNAL_MAIL_DOMAIN = "grid-code.tech"
INTERNAL_MAIL_TO = "laia@grid-code.tech"


@dataclass(frozen=True)
class InternalCapability:
    trigger_id: str
    label: str
    mail_subject: str
    mail_body: str
    skill_name: str
    skill_group: str
    keywords: Sequence[str]

    def mailto_url(self, to_email: str = INTERNAL_MAIL_TO) -> str:
        subject = quote(self.mail_subject, safe="")
        body = quote(self.mail_body, safe="")
        return f"mailto:{to_email}?subject={subject}&body={body}"

    def to_dict(self, index: int, to_email: str = INTERNAL_MAIL_TO) -> Dict[str, Any]:
        return {
            "index": index,
            "trigger_id": self.trigger_id,
            "label": self.label,
            "skill_name": self.skill_name,
            "skill_group": self.skill_group,
            "keywords": list(self.keywords),
            "mail_subject": self.mail_subject,
            "mail_body": self.mail_body,
            "mailto_url": self.mailto_url(to_email),
            "text_link": f"> {index}) {self.label}",
            "plain_trigger": self.mail_body,
        }


VERIFIED_INTERNAL_CAPABILITIES: List[InternalCapability] = [
    InternalCapability(
        trigger_id="internal_meet",
        label="Hacer una meet",
        mail_subject="[TRIGGER] Meet telemática para coordinación",
        mail_body="Laia, necesito que generes una meet telemática para poder reunirnos por Teams. Los datos de la meet y las personas serán: ... Gracias.",
        skill_name="calendar-meet-host-gridcode",
        skill_group="calendar-meet-coordination",
        keywords=("meet", "reunión", "reunion", "teams", "calendar", "videollamada"),
    ),
    InternalCapability(
        trigger_id="calendar_task_event",
        label="Consignar una tarea o evento en calendario",
        mail_subject="[TRIGGER] Tarea o evento en calendario",
        mail_body="Laia, necesito que consignes una tarea o evento en calendario con estos datos: ... Gracias.",
        skill_name="calendar-meet-host-gridcode",
        skill_group="calendar-meet-coordination",
        keywords=("calendario", "evento", "tarea", "agenda", "calendar", "recordatorio"),
    ),
    InternalCapability(
        trigger_id="drive_search",
        label="Buscar algun archivo en Drive",
        mail_subject="[TRIGGER] Búsqueda de archivo en Drive",
        mail_body="Laia, necesito que busques un archivo en Drive. Los datos de búsqueda son: ... Gracias.",
        skill_name="gridcode-drive-api-first-governance",
        skill_group="drive-document-retrieval",
        keywords=("drive", "archivo", "documento", "carpeta", "buscar", "share"),
    ),
    InternalCapability(
        trigger_id="commercial_technical_admin_report",
        label="Hacer informes o reportes comerciales tecnicos o administrativos",
        mail_subject="[TRIGGER] Informe o reporte comercial, técnico o administrativo",
        mail_body="Laia, necesito que generes un informe o reporte comercial, técnico o administrativo con estos datos: ... Gracias.",
        skill_name="gridcode-preliminary-analysis-report",
        skill_group="report-generation",
        keywords=("informe", "reporte", "comercial", "técnico", "tecnico", "administrativo", "resumen"),
    ),
    InternalCapability(
        trigger_id="on_site_charger_report",
        label="Hacer reportes para cargadores que se han de visitar on-site",
        mail_subject="[TRIGGER] Reporte on-site de cargadores",
        mail_body="Laia, necesito que generes un reporte para los cargadores que se han de visitar on-site. Los datos son: ... Gracias.",
        skill_name="gridcode-preliminary-analysis-report",
        skill_group="report-generation",
        keywords=("on-site", "on site", "visitar", "cargador", "cargadores", "inspección", "inspeccion"),
    ),
    InternalCapability(
        trigger_id="remote_logs_report",
        label="Hacer informes remotos sobre los logs de eventos de los cargadores",
        mail_subject="[TRIGGER] Informe remoto de logs de cargadores",
        mail_body="Laia, necesito que generes un informe remoto sobre los logs de eventos de los cargadores. Los datos son: ... Gracias.",
        skill_name="ocpp-log-unpack-7d-analysis",
        skill_group="audit-trace",
        keywords=("logs", "eventos", "remoto", "telemetría", "telemetria", "ocpp", "registro"),
    ),
    InternalCapability(
        trigger_id="ocpp_certificate",
        label="Hacer certificados de validacion OCPP",
        mail_subject="[TRIGGER] Certificado de validación OCPP",
        mail_body="Laia, necesito que generes un certificado de validación OCPP con estos datos: ... Gracias.",
        skill_name="certificate-generation",
        skill_group="certificate-generation",
        keywords=("certificado", "validación", "validacion", "ocpp", "certificación", "certificacion"),
    ),
]


def is_internal_team_email(email: str) -> bool:
    value = (email or "").strip().lower()
    return value.endswith(f"@{INTERNAL_MAIL_DOMAIN}")


def _score_capability(query: str, capability: InternalCapability) -> int:
    q = (query or "").lower()
    score = 0
    for keyword in capability.keywords:
        if keyword and keyword.lower() in q:
            score += 3 if len(keyword) > 4 else 2
    if capability.trigger_id in q:
        score += 5
    return score


def select_internal_capability(query: str) -> Dict[str, Any]:
    normalized = (query or "").strip().lower()
    ranked = sorted(
        (
            {
                **cap.to_dict(index=i + 1),
                "score": _score_capability(normalized, cap),
            }
            for i, cap in enumerate(VERIFIED_INTERNAL_CAPABILITIES)
        ),
        key=lambda item: item["score"],
        reverse=True,
    )
    selected = ranked[0] if ranked and ranked[0]["score"] > 0 else None
    return {
        "query": query,
        "selected": selected,
        "candidates": ranked,
    }


def _selected_item(items: List[Dict[str, Any]], selected_trigger: str | None) -> Dict[str, Any] | None:
    if not selected_trigger:
        return None
    return next((item for item in items if item["trigger_id"] == selected_trigger), None)


def build_internal_capabilities_block(name: str = "Lore", to_email: str = INTERNAL_MAIL_TO, selected_trigger: str | None = None) -> Dict[str, Any]:
    items = [cap.to_dict(index=i + 1, to_email=to_email) for i, cap in enumerate(VERIFIED_INTERNAL_CAPABILITIES)]
    lines = ["Podes contar conmigo para:"]
    for item in items:
        lines.append(f"> {item['index']}) {item['label']} - {item['mailto_url']}")

    selected = _selected_item(items, selected_trigger)

    return {
        "enabled": True,
        "mode": "full",
        "recipient_name": name,
        "recipient_email": to_email,
        "count": len(items),
        "items": items,
        "selected": selected,
        "text": "\n".join(lines),
    }


def build_internal_capabilities_compact_block(name: str = "Lore", to_email: str = INTERNAL_MAIL_TO, selected_trigger: str | None = None) -> Dict[str, Any]:
    items = [cap.to_dict(index=i + 1, to_email=to_email) for i, cap in enumerate(VERIFIED_INTERNAL_CAPABILITIES)]
    compact_map = [
        (1, "Hacer una meet"),
        (2, "Consignar una tarea o evento en calendario"),
        (3, "Buscar algun archivo en Drive"),
        (4, "Hacer informes o reportes comerciales tecnicos o administrativos"),
        (5, "Hacer reportes para cargadores que se han de visitar on-site"),
        (6, "Hacer informes remotos sobre los logs de eventos de los cargadores"),
        (7, "Hacer certificados de validacion OCPP"),
    ]
    lines = ["Podes contar conmigo para:"]
    for index, label in compact_map:
        lines.append(f"> {index}) {label}")

    selected = _selected_item(items, selected_trigger)

    return {
        "enabled": True,
        "mode": "compact",
        "recipient_name": name,
        "recipient_email": to_email,
        "count": len(items),
        "items": items,
        "selected": selected,
        "text": "\n".join(lines),
        "html": "<div>" + "<br/>".join(escape(line) for line in lines) + "</div>",
    }


def build_internal_capabilities_html_block(name: str = "Lore", to_email: str = INTERNAL_MAIL_TO, selected_trigger: str | None = None) -> Dict[str, Any]:
    block = build_internal_capabilities_compact_block(name=name, to_email=to_email, selected_trigger=selected_trigger)
    html_lines = [
        '<div style="font-family:Arial,sans-serif; line-height:1.55; color:#222;">',
        '<p style="margin:0 0 12px 0; font-weight:600;">Podes contar conmigo para:</p>',
        '<table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:collapse; width:100%;">',
    ]
    for item in block["items"]:
        label = escape(item["label"])
        href = escape(item["mailto_url"], quote=True)
        html_lines.append(
            '<tr>'
            f'<td style="padding:4px 0; vertical-align:top; white-space:nowrap;">&gt;</td>'
            f'<td style="padding:4px 0;">'
            f'<a href="{href}" style="color:#0b57d0; text-decoration:none;">{item["index"]}) {label}</a>'
            '</td>'
            '</tr>'
        )
    html_lines.append('</table>')
    html_lines.append('</div>')
    block["html"] = "".join(html_lines)
    block["mode"] = "compact-html"
    return block
