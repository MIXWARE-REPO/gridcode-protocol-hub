#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


@dataclass
class InputData:
    base_url: str
    username: str
    password: str
    charger_name: str
    charger_id: str
    charger_type: str = "AC"
    phase: str = "Single-Phase"
    headless: bool = True


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_input(path: Path) -> InputData:
    raw = json.loads(path.read_text(encoding="utf-8"))
    required = ["base_url", "username", "password", "charger_name", "charger_id"]
    miss = [k for k in required if not raw.get(k)]
    if miss:
        raise ValueError(f"missing_required_fields:{','.join(miss)}")
    return InputData(
        base_url=raw["base_url"],
        username=raw["username"],
        password=raw["password"],
        charger_name=raw["charger_name"],
        charger_id=str(raw["charger_id"]),
        charger_type=raw.get("charger_type", "AC"),
        phase=raw.get("phase", "Single-Phase"),
        headless=bool(raw.get("headless", True)),
    )


def sel_try(page, selectors: list[str]):
    for s in selectors:
        loc = page.locator(s).first
        if loc.count() > 0:
            return loc, s
    return None, None


def screenshot(page, out_dir: Path, name: str, ev: dict[str, list[str]]):
    p = out_dir / f"{name}.png"
    page.screenshot(path=str(p), full_page=True)
    ev["screenshots"].append(str(p))
    h = out_dir / f"{name}.html"
    h.write_text(page.content(), encoding="utf-8")
    ev["html"].append(str(h))


def run(inp: InputData, run_dir: Path) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    ev_dir = run_dir / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)

    out: dict[str, Any] = {
        "started_at": now_iso(),
        "status": "error",
        "steps": [],
        "warnings": [],
        "errors": [],
        "ocpp": {"url": None, "source": "CONFIGURATIONS/CONNECTION SETTINGS/OCPP URL"},
        "charger": {
            "name": inp.charger_name,
            "id": inp.charger_id,
            "type": inp.charger_type,
            "phase": inp.phase,
            "created": False,
            "success_message_seen": False,
        },
        "evidence": {"screenshots": [], "html": []},
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=inp.headless)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.set_default_timeout(30000)
        try:
            page.goto(inp.base_url)
            page.wait_for_timeout(1200)

            u, _ = sel_try(page, ['input[placeholder="Username"]', 'input[name="username"]', 'input[type="text"]'])
            pw, _ = sel_try(page, ['input[placeholder="Password"]', 'input[name="password"]', 'input[type="password"]'])
            sb, _ = sel_try(page, ['button:has-text("SUBMIT")', 'button[type="submit"]'])
            if not (u and pw and sb):
                out["errors"].append("login_selectors_not_found")
                screenshot(page, ev_dir, "01_login_failed_selectors", out["evidence"])
                return out

            u.fill(inp.username)
            pw.fill(inp.password)
            sb.click()
            page.wait_for_timeout(2500)
            out["steps"].append("login_submit")
            screenshot(page, ev_dir, "02_after_login", out["evidence"])

            my_chargers, _ = sel_try(page, ['a:has-text("MY CHARGERS")', 'a:has-text("My Chargers")'])
            if not my_chargers:
                out["errors"].append("login_failed_or_dashboard_not_loaded")
                return out
            my_chargers.click()
            page.wait_for_timeout(1200)
            out["steps"].append("open_my_chargers")

            add_btn, _ = sel_try(page, ['button:has-text("ADD CHARGER")', 'button:has-text("Add Charger")'])
            if not add_btn:
                out["errors"].append("add_charger_button_not_found")
                screenshot(page, ev_dir, "03_missing_add_charger", out["evidence"])
                return out
            add_btn.click()
            page.wait_for_timeout(900)
            out["steps"].append("open_add_charger_modal")

            name_in, _ = sel_try(page, ['input[placeholder*="Parking"]'])
            id_in, _ = sel_try(page, ['input[placeholder*="P01"]'])
            if not (name_in and id_in):
                out["errors"].append("add_charger_fields_not_found")
                screenshot(page, ev_dir, "04_missing_charger_fields", out["evidence"])
                return out
            name_in.fill(inp.charger_name)
            id_in.fill(inp.charger_id)

            # Ensure type and phase expected
            type_cb, _ = sel_try(page, ['div:has(> [role="combobox"]):has-text("AC")', '[role="combobox"]:has-text("AC")'])
            if not type_cb and inp.charger_type.upper() == "AC":
                out["warnings"].append("type_combobox_not_explicitly_verified")

            phase_cb, _ = sel_try(page, ['[role="combobox"]:has-text("Single-Phase")'])
            if not phase_cb and inp.phase.lower().startswith("single"):
                out["warnings"].append("phase_combobox_not_explicitly_verified")

            add_final, _ = sel_try(page, ['button:has-text("Add")'])
            if not add_final:
                out["errors"].append("final_add_button_not_found")
                screenshot(page, ev_dir, "05_missing_final_add", out["evidence"])
                return out
            add_final.click()
            page.wait_for_timeout(1400)
            out["steps"].append("submit_add_charger")

            body = page.inner_text("body")
            if "It's all ok!" in body or "Its all ok" in body:
                out["charger"]["success_message_seen"] = True
                out["charger"]["created"] = True
            else:
                out["warnings"].append("success_message_not_seen")

            # close modal if present
            cancel, _ = sel_try(page, ['button:has-text("Cancel")'])
            if cancel:
                cancel.click()
                page.wait_for_timeout(400)

            screenshot(page, ev_dir, "06_after_create", out["evidence"])

            # OCPP URL
            cfg, _ = sel_try(page, ['a:has-text("CONFIGURATIONS")'])
            if not cfg:
                out["errors"].append("configurations_menu_not_found")
                return out
            cfg.click()
            page.wait_for_timeout(1200)
            out["steps"].append("open_configurations")

            conn, _ = sel_try(page, ['a:has-text("CONNECTION SETTINGS")'])
            if conn:
                conn.click()
                page.wait_for_timeout(1000)
            out["steps"].append("open_connection_settings")

            ocpp_code, _ = sel_try(page, ['code'])
            if ocpp_code:
                txt = (ocpp_code.inner_text() or "").strip()
                if txt.startswith("ws://") or txt.startswith("wss://"):
                    out["ocpp"]["url"] = txt
            if not out["ocpp"]["url"]:
                text = page.inner_text("body")
                import re
                m = re.search(r"wss?://[^\s]+", text)
                if m:
                    out["ocpp"]["url"] = m.group(0)

            screenshot(page, ev_dir, "07_ocpp_section", out["evidence"])

            if out["charger"]["created"] and out["ocpp"]["url"]:
                out["status"] = "ok"
            elif out["charger"]["created"]:
                out["status"] = "partial"
                out["warnings"].append("ocpp_url_not_found")
            else:
                out["status"] = "error"

            return out

        except Exception as e:
            out["errors"].append(f"runtime_error:{e}")
            screenshot(page, ev_dir, "99_exception", out["evidence"])
            return out
        finally:
            out["finished_at"] = now_iso()
            ctx.close()
            browser.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="CPMS WINGS: crear cargador AC monofásico y leer OCPP URL")
    ap.add_argument("--input", required=True, help="JSON de entrada")
    ap.add_argument("--output", required=True, help="JSON de salida")
    ap.add_argument("--out-base", default="/home/laia/gridcode-protocol-hub/out/cpms-wings-create-charger")
    args = ap.parse_args()

    inp = load_input(Path(args.input))
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{inp.charger_id}"
    run_dir = Path(args.out_base) / run_id

    result = run(inp, run_dir)
    result["artifacts"] = {"run_dir": str(run_dir)}

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": result.get("status"), "output": str(out_path)}, ensure_ascii=False))
    return 0 if result.get("status") in ("ok", "partial") else 1


if __name__ == "__main__":
    raise SystemExit(main())
