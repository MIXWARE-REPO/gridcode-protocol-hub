from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ProtocolResult:
    success: bool
    protocol_id: str
    output: Dict[str, Any]
    errors: list[str]
