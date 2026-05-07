from __future__ import annotations

from typing import List, Optional


LAIA_EMAIL = "laia@grid-code.tech"


def normalize_emails(values: List[str] | None) -> set[str]:
    return {str(x).strip().lower() for x in (values or []) if str(x).strip()}


def classify_priority(to_list: List[str] | None, cc_list: List[str] | None, laia_email: str = LAIA_EMAIL) -> Optional[str]:
    """
    Regla trazable y única:
    - P1: Laia en TO (destinataria directa)
    - P2: Laia en CC (copia)
    - None: no participa
    """
    le = laia_email.strip().lower()
    to_norm = normalize_emails(to_list)
    cc_norm = normalize_emails(cc_list)

    if le in to_norm:
        return "P1"
    if le in cc_norm:
        return "P2"
    return None
