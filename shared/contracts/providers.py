from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


@dataclass
class EmailMessage:
    id: str
    from_email: str
    from_name: str
    to: List[str]
    cc: List[str]
    subject: str
    body: str
    timestamp: str
    thread_id: str = ""
    is_forward: bool = False


class InboxProvider(Protocol):
    """Abstracción de lectura/escritura de correo (Gmail u otro proveedor)."""

    def fetch_inbox(self, limit: int = 50) -> List[EmailMessage]:
        ...

    def fetch_thread(self, thread_id: str) -> List[EmailMessage]:
        ...

    def send_reply(self, thread_id: str, subject: str, body: str, to: List[str], cc: List[str] | None = None) -> Dict[str, Any]:
        ...


class ContactProvider(Protocol):
    """Abstracción para búsqueda/actualización de contactos (Google Contacts u otro)."""

    def find_contact(self, email: str) -> Dict[str, Any] | None:
        ...

    def create_contact(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def minimal_update_contact(self, contact_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def full_update_contact(self, contact_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...
