from __future__ import annotations

from typing import Any, Dict

from shared.policies.laia_mail_router_policy_v1 import evaluate_mail_route


def run_laia_mail_router(payload: Dict[str, Any]) -> Dict[str, Any]:
    return evaluate_mail_route(payload)


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    return run_laia_mail_router(payload)
