from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


@dataclass
class AttachmentRef:
    filename: str
    mime_type: str
    size_bytes: int
    source: str  # gmail|drive|local|unknown
    message_id: str = ""
    part_id: str = ""
    drive_file_id: str = ""
    drive_url: str = ""
    local_path: str = ""


class AttachmentProvider(Protocol):
    """Proveedor de adjuntos desacoplado del motor de negocio."""

    def list_message_attachments(self, message_id: str) -> List[AttachmentRef]:
        ...

    def fetch_attachment_bytes(self, message_id: str, part_id: str) -> bytes:
        ...

    def upload_to_drive(self, filename: str, content: bytes, folder_id: str | None = None) -> Dict[str, Any]:
        ...

    def resolve_drive_file(self, drive_file_id: str) -> Dict[str, Any]:
        ...
