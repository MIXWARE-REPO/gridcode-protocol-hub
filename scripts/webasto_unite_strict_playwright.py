#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from shared.orchestration.charger_webui_playwright_v1 import (
    ChargerRunConfig,
    run_playwright_session,
    save_run_json,
)

VERSION = "webasto_unite_strict_playwright_v1"
ROOT = Path("/home/laia/gridcode-protocol-hub")
DEFAULT_OUT_BASE = ROOT / "out" / "webasto-unite-runs"


@dataclass
class RunInput:
    run_id: str
    charger_ip: str
    charger_label: str
    username: str
    password: str
    ocpp_endpoint: str
    free_charge_mode_active: bool
    set_static_network: bool
    static_ip: str | None
    netmask: str
    gateway: str | None
    dns_primary: str
    download_logs: bool
    download_wait_seconds: int
    do_soft_reset: bool
    do_hard_reset: bool
    headless: bool


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_input(path: Path) -> RunInput:
    raw = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "run_id", "charger_ip", "charger_label", "username", "password",
        "ocpp_endpoint", "free_charge_mode_active",
    ]
    for k in required:
        if k not in raw:
            raise ValueError(f"missing_required_field:{k}")

    return RunInput(
        run_id=raw["run_id"],
        charger_ip=raw["charger_ip"],
        charger_label=raw["charger_label"],
        username=raw["username"],
        password=raw["password"],
        ocpp_endpoint=raw["ocpp_endpoint"],
        free_charge_mode_active=bool(raw["free_charge_mode_active"]),
        set_static_network=bool(raw.get("set_static_network", False)),
        static_ip=raw.get("static_ip"),
        netmask=raw.get("netmask", "255.255.255.0"),
        gateway=raw.get("gateway"),
        dns_primary=raw.get("dns_primary", "8.8.8.8"),
        download_logs=bool(raw.get("download_logs", True)),
        download_wait_seconds=int(raw.get("download_wait_seconds", 240)),
        do_soft_reset=bool(raw.get("do_soft_reset", False)),
        do_hard_reset=bool(raw.get("do_hard_reset", False)),
        headless=bool(raw.get("headless", True)),
    )


def _validate_business_rules(inp: RunInput) -> list[str]:
    errs: list[str] = []
    if not inp.charger_ip:
        errs.append("charger_ip_empty")
    if inp.set_static_network and (not inp.static_ip or not inp.gateway):
        errs.append("static_network_missing_fields")
    if inp.download_wait_seconds < 30:
        errs.append("download_wait_too_short_min_30")
    return errs


def _build_run_folder(base: Path, inp: RunInput) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = base / f"{stamp}_{inp.run_id}_{inp.charger_label}_{inp.charger_ip.replace('.', '_')}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "downloads").mkdir(exist_ok=True)
    return folder


def _compose_ocpp_updates(inp: RunInput) -> Dict[str, str]:
    # Regla operativa consolidada: si backend gestiona autorización vía OCPP,
    # Free Charge Mode Active debe permanecer en false.
    return {
        "freeChargeModeActive": "true" if inp.free_charge_mode_active else "false",
    }


def run(inp: RunInput, out_dir: Path) -> Dict[str, Any]:
    started = _now_iso()
    errors = _validate_business_rules(inp)
    if errors:
        return {
            "version": VERSION,
            "status": "error",
            "error_code": "INVALID_INPUT",
            "errors": errors,
            "started_at": started,
            "ended_at": _now_iso(),
        }

    run_dir = _build_run_folder(out_dir, inp)

    config = ChargerRunConfig(
        ip=inp.charger_ip,
        username=inp.username,
        password=inp.password,
        target_endpoint=inp.ocpp_endpoint,
        ocpp_updates=_compose_ocpp_updates(inp),
        download_logs=inp.download_logs,
        reboot=inp.do_hard_reset,
        allow_unsafe_actions=inp.do_hard_reset,
        timeout_ms=max(inp.download_wait_seconds, 30) * 1000,
        headless=inp.headless,
    )

    webui_result = run_playwright_session(config=config, out_dir=run_dir)
    webui_json = save_run_json(webui_result, run_dir / "01_webui_result.json")

    artifacts = {
        "run_dir": str(run_dir),
        "webui_result_json": str(webui_json),
        "downloads": webui_result.get("evidence", {}).get("downloads", []),
        "screenshots": webui_result.get("evidence", {}).get("screenshots", []),
    }

    status = "ok" if webui_result.get("ok") else "error"
    output = {
        "version": VERSION,
        "status": status,
        "started_at": started,
        "ended_at": _now_iso(),
        "run_id": inp.run_id,
        "charger": {
            "label": inp.charger_label,
            "ip": inp.charger_ip,
        },
        "applied": {
            "ocpp_endpoint": inp.ocpp_endpoint,
            "free_charge_mode_active": inp.free_charge_mode_active,
            "set_static_network_requested": inp.set_static_network,
            "static_network": {
                "static_ip": inp.static_ip,
                "netmask": inp.netmask,
                "gateway": inp.gateway,
                "dns_primary": inp.dns_primary,
            },
            "do_soft_reset_requested": inp.do_soft_reset,
            "do_hard_reset_requested": inp.do_hard_reset,
        },
        "result": {
            "actions": webui_result.get("actions", []),
            "warnings": webui_result.get("warnings", []),
            "errors": webui_result.get("errors", []),
            "ocpp_before": webui_result.get("ocpp_before", {}),
            "ocpp_after": webui_result.get("ocpp_after", {}),
        },
        "artifacts": artifacts,
    }

    (run_dir / "00_summary.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Procedimiento estricto Webasto/Unite vía Playwright")
    parser.add_argument("--input", required=True, help="JSON de entrada")
    parser.add_argument("--output", required=True, help="JSON de salida")
    parser.add_argument("--out-base", default=str(DEFAULT_OUT_BASE), help="Directorio base de ejecuciones")
    args = parser.parse_args()

    inp = _load_input(Path(args.input))
    out = run(inp, Path(args.out_base))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": out.get("status"), "output": str(out_path)}, ensure_ascii=False))
    return 0 if out.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
