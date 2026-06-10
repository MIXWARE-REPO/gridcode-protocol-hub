from typing import Any, Dict

from shared.orchestration.laia_mail_router_v1 import run_laia_mail_router

PROTOCOL_ID = "laia_mail_router_v1"


def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    out = run_laia_mail_router(inputs)
    out["protocol_id"] = PROTOCOL_ID
    return out
