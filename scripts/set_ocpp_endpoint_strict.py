#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from shared.orchestration.charger_webui_playwright_v1 import (
    ChargerRunConfig,
    run_playwright_session,
)

ROOT = Path("/home/laia/gridcode-protocol-hub")
DEFAULT_OUT_BASE = ROOT / "out" / "ocpp-endpoint-runs"


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_run_dir(ip: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = DEFAULT_OUT_BASE / f"{stamp}_{ip.replace('.', '_')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def run(ip: str, password: str, endpoint: str, username: str = "admin", timeout_ms: int = 20000) -> dict:
    run_dir = _build_run_dir(ip)
    result = {
        "ip": ip,
        "target_endpoint": endpoint,
        "started_at": iso_now(),
        "status": "FAIL",
        "before_endpoint": None,
        "after_endpoint": None,
        "save_clicked": False,
        "save_disabled_after": None,
        "run_dir": str(run_dir),
        "error": None,
    }

    config = ChargerRunConfig(
        ip=ip,
        username=username,
        password=password,
        target_endpoint=endpoint,
        timeout_ms=timeout_ms,
        headless=True,
    )

    try:
        webui_result = run_playwright_session(config=config, out_dir=run_dir)
        result["before_endpoint"] = webui_result.get("ocpp_before", {}).get("centralSystemAddress")
        result["after_endpoint"] = webui_result.get("ocpp_after", {}).get("centralSystemAddress")
        result["save_clicked"] = "save_ocpp" in webui_result.get("actions", [])
        result["save_disabled_after"] = None

        if webui_result.get("ok") and result["after_endpoint"] == endpoint:
            result["status"] = "OK"
        else:
            result["status"] = "FAIL"
            errors = webui_result.get("errors", [])
            if errors:
                result["error"] = "; ".join(errors)
            elif result["after_endpoint"] != endpoint:
                result["error"] = "Endpoint no persistió tras verificación"
            else:
                result["error"] = "Ejecución Playwright no marcada como ok"

        result["webui_result"] = webui_result
    except Exception as e:
        result["error"] = str(e)
    finally:
        result["finished_at"] = iso_now()

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Cambio estricto de endpoint OCPP con selectores estáticos y verificación de persistencia")
    ap.add_argument("--ip", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--username", default="admin")
    ap.add_argument("--timeout-ms", type=int, default=20000)
    args = ap.parse_args()

    out = run(args.ip, args.password, args.endpoint, args.username, args.timeout_ms)
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out.get("status") == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
