from __future__ import annotations

from typing import Any, Dict, List

# Rutas/fuentes canónicas aunque luego se ajusten en implementación real.
ATTACHMENT_SOURCES = {
    "gmail_parts": "message.payload.parts[].body.attachmentId",
    "drive_links_in_body": "https://drive.google.com/...",
    "drive_api_file": "drive.files.get(fileId)",
}

DEFAULT_DRIVE_POLICY = {
    "enabled": True,
    "default_folder_hint": "GridCode/EmailAttachments/Inbox",
    "naming": "{date}_{sender}_{subject}_{filename}",
}


def detect_attachment_sources(email_record: Dict[str, Any]) -> Dict[str, Any]:
    body = (email_record.get("body") or "")
    has_drive_link = "drive.google.com" in body
    has_parts = bool(email_record.get("attachments") or email_record.get("attachment_ids"))

    return {
        "has_parts": has_parts,
        "has_drive_link": has_drive_link,
        "source_priority": ["gmail_parts", "drive_links_in_body", "drive_api_file"],
        "canonical_paths": ATTACHMENT_SOURCES,
    }


def build_attachment_resolution_plan(email_record: Dict[str, Any], category: str = "general") -> Dict[str, Any]:
    src = detect_attachment_sources(email_record)

    return {
        "protocol": "email_attachments_router_v1",
        "category": category,
        "drive_policy": DEFAULT_DRIVE_POLICY,
        "resolution": src,
        "next_actions": [
            "listar adjuntos del mensaje vía provider",
            "si hay drive link, resolver file_id y metadatos",
            "subir/custodiar en carpeta Drive objetivo cuando aplique",
            "dejar referencia trazable en learning/log",
        ],
    }
