from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
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
    ),
    InternalCapability(
        trigger_id="calendar_task_event",
        label="Consignar una tarea o evento en calendario",
        mail_subject="[TRIGGER] Tarea o evento en calendario",
        mail_body="Laia, necesito que consignes una tarea o evento en calendario con estos datos: ... Gracias.",
        skill_name="calendar-meet-host-gridcode",
        skill_group="calendar-meet-coordination",
    ),
    InternalCapability(
        trigger_id="drive_search",
        label="Buscar algun archivo en Drive",
        mail_subject="[TRIGGER] Búsqueda de archivo en Drive",
        mail_body="Laia, necesito que busques un archivo en Drive. Los datos de búsqueda son: ... Gracias.",
        skill_name="gridcode-drive-api-first-governance",
        skill_group="drive-document-retrieval",
    ),
    InternalCapability(
        trigger_id="commercial_technical_admin_report",
        label="Hacer informes o reportes comerciales tecnicos o administrativos",
        mail_subject="[TRIGGER] Informe o reporte comercial, técnico o administrativo",
        mail_body="Laia, necesito que generes un informe o reporte comercial, técnico o administrativo con estos datos: ... Gracias.",
        skill_name="gridcode-preliminary-analysis-report",
        skill_group="report-generation",
    ),
    InternalCapability(
        trigger_id="on_site_charger_report",
        label="Hacer reportes para cargadores que se han de visitar on-site",
        mail_subject="[TRIGGER] Reporte on-site de cargadores",
        mail_body="Laia, necesito que generes un reporte para los cargadores que se han de visitar on-site. Los datos son: ... Gracias.",
        skill_name="gridcode-preliminary-analysis-report",
        skill_group="report-generation",
    ),
    InternalCapability(
        trigger_id="remote_logs_report",
        label="Hacer informes remotos sobre los logs de eventos de los cargadores",
        mail_subject="[TRIGGER] Informe remoto de logs de cargadores",
        mail_body="Laia, necesito que generes un informe remoto sobre los logs de eventos de los cargadores. Los datos son: ... Gracias.",
        skill_name="ocpp-log-unpack-7d-analysis",
        skill_group="audit-trace",
    ),
    InternalCapability(
        trigger_id="ocpp_certificate",
        label="Hacer certificados de validacion OCPP",
        mail_subject="[TRIGGER] Certificado de validación OCPP",
        mail_body="Laia, necesito que generes un certificado de validación OCPP con estos datos: ... Gracias.",
        skill_name="certificate-generation",
        skill_group="certificate-generation",
    ),
]


def is_internal_team_email(email: str) -> bool:
    value = (email or "").strip().lower()
    return value.endswith(f"@{INTERNAL_MAIL_DOMAIN}")


def build_internal_capabilities_block(name: str = "Lore", to_email: str = INTERNAL_MAIL_TO) -> Dict[str, Any]:
    items = [cap.to_dict(index=i + 1, to_email=to_email) for i, cap in enumerate(VERIFIED_INTERNAL_CAPABILITIES)]
    lines = ["Podes contar conmigo para:"]
    for item in items:
        lines.append(f"> {item['index']}) {item['label']} - {item['mailto_url']}")
    return {
        "enabled": True,
        "recipient_name": name,
        "recipient_email": to_email,
        "count": len(items),
        "items": items,
        "text": "\n".join(lines),
    }
