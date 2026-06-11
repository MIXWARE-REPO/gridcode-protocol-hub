#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from shared.orchestration.charger_webui_playwright_v1 import (
    ChargerRunConfig,
    run_playwright_session,
    save_run_json,
)

VERSION = "webasto_unite_cpms_unified_playwright_v2"
ROOT = Path("/home/laia/gridcode-protocol-hub")
DEFAULT_OUT_BASE = ROOT / "out" / "webasto-unite-cpms-unified"


@dataclass
class ChargerInput:
    ip: str
    username: str
    password: str
    ocpp_endpoint: str
    free_charge_mode_active: bool = False
    download_logs: bool = True
    download_wait_seconds: int = 240
    hard_reset: bool = False


@dataclass
class CpmsInput:
    base_url: str
    username: str
    password: str
    expected_instance_ip: Optional[str] = None
    create_charger: bool = False
    charger_id: Optional[str] = None
    charger_name: Optional[str] = None
    connector_count: Optional[int] = 1
    ocpp_version: Optional[str] = "1.6"
    priority: Optional[str] = "High"
    auth_mode: Optional[str] = "backend_cloud"  # local_cpms | backend_cloud | charger_local
    create_user: bool = False
    user_full_name: Optional[str] = None
    user_username: Optional[str] = None
    user_password: Optional[str] = None
    user_tag_id: Optional[str] = None
    user_company: Optional[str] = None
    user_priority: Optional[str] = "High"
    user_role: Optional[str] = "user"


@dataclass
class UnifiedInput:
    run_id: str
    headless: bool
    charger: ChargerInput
    cpms: CpmsInput


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_input(path: Path) -> UnifiedInput:
    raw = json.loads(path.read_text(encoding="utf-8"))
    for k in ["run_id", "charger", "cpms"]:
        if k not in raw:
            raise ValueError(f"missing_required_field:{k}")

    charger = ChargerInput(**raw["charger"])
    cpms = CpmsInput(**raw["cpms"])
    return UnifiedInput(
        run_id=raw["run_id"],
        headless=bool(raw.get("headless", True)),
        charger=charger,
        cpms=cpms,
    )


def validate(inp: UnifiedInput) -> list[str]:
    errs: list[str] = []
    if not inp.charger.ip:
        errs.append("charger_ip_empty")
    if not inp.cpms.base_url:
        errs.append("cpms_base_url_empty")
    if inp.cpms.create_user:
        if not inp.cpms.user_username or not inp.cpms.user_password:
            errs.append("cpms_user_missing_credentials")
        if inp.cpms.user_password and len(inp.cpms.user_password) < 6:
            errs.append("cpms_user_password_min_6")
    if inp.cpms.create_charger and not inp.cpms.charger_id:
        errs.append("cpms_create_charger_missing_id")
    return errs


def safe_mkdir(base: Path, run_id: str, charger_ip: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    d = base / f"{stamp}_{run_id}_{charger_ip.replace('.', '_')}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_charger_phase(inp: UnifiedInput, out_dir: Path) -> Dict[str, Any]:
    config = ChargerRunConfig(
        ip=inp.charger.ip,
        username=inp.charger.username,
        password=inp.charger.password,
        target_endpoint=inp.charger.ocpp_endpoint,
        ocpp_updates={"freeChargeModeActive": "true" if inp.charger.free_charge_mode_active else "false"},
        download_logs=inp.charger.download_logs,
        reboot=inp.charger.hard_reset,
        allow_unsafe_actions=inp.charger.hard_reset,
        timeout_ms=max(inp.charger.download_wait_seconds, 30) * 1000,
        headless=inp.headless,
    )
    result = run_playwright_session(config=config, out_dir=out_dir / "charger_phase")
    save_run_json(result, out_dir / "charger_phase" / "01_charger_result.json")
    return result


def _sel_try(page, selectors: list[str]):
    for s in selectors:
        loc = page.locator(s).first
        if loc.count() > 0:
            return loc, s
    return None, None


def run_cpms_phase(inp: UnifiedInput, out_dir: Path) -> Dict[str, Any]:
    from playwright.sync_api import sync_playwright

    cp = inp.cpms
    ev_dir = out_dir / "cpms_phase" / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)

    res: Dict[str, Any] = {
        "started_at": now_iso(),
        "actions": [],
        "warnings": [],
        "errors": [],
        "evidence": {"screenshots": [], "html": []},
        "metrics_snapshot": {},
        "settings_snapshot": {},
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=inp.headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(25000)

        try:
            page.goto(cp.base_url)
            user_loc, _ = _sel_try(page, ['input[name="username"]', 'input[type="text"]'])
            pass_loc, _ = _sel_try(page, ['input[name="password"]', 'input[type="password"]'])
            btn_loc, _ = _sel_try(page, ['button[type="submit"]', 'input[type="submit"]', 'button:has-text("Login")'])
            if user_loc and pass_loc and btn_loc:
                user_loc.fill(cp.username)
                pass_loc.fill(cp.password)
                btn_loc.click()
                page.wait_for_timeout(1200)
                res["actions"].append("cpms_login")
            else:
                res["warnings"].append("cpms_login_selectors_partial")

            s1 = ev_dir / "01_after_login.png"
            page.screenshot(path=str(s1), full_page=True)
            res["evidence"]["screenshots"].append(str(s1))
            h1 = ev_dir / "01_after_login.html"
            h1.write_text(page.content(), encoding="utf-8")
            res["evidence"]["html"].append(str(h1))

            # Chargers tab
            ch_tab, _ = _sel_try(page, ['a:has-text("Chargers")', 'button:has-text("Chargers")'])
            if ch_tab:
                ch_tab.click()
                page.wait_for_timeout(700)
                res["actions"].append("open_chargers_tab")

            if cp.create_charger:
                add_btn, _ = _sel_try(page, ['button:has-text("Add")', 'button:has-text("New")'])
                if add_btn:
                    add_btn.click()
                    page.wait_for_timeout(600)
                    res["actions"].append("create_charger_open_form")
                # Best effort fields
                fld_map = {
                    "name": cp.charger_name or f"CHG-{cp.charger_id}",
                    "id": cp.charger_id,
                    "connector": str(cp.connector_count or 1),
                }
                for key, val in fld_map.items():
                    if not val:
                        continue
                    loc, _ = _sel_try(page, [f'input[name="{key}"]', f'input[id*="{key}"]'])
                    if loc:
                        loc.fill(val)
                    else:
                        res["warnings"].append(f"cpms_charger_field_not_found:{key}")

                save_btn, _ = _sel_try(page, ['button:has-text("Save")', 'button:has-text("Create")'])
                if save_btn:
                    save_btn.click()
                    page.wait_for_timeout(1000)
                    res["actions"].append("create_charger_submit")
                else:
                    res["warnings"].append("cpms_charger_save_not_found")

            # Metrics tab snapshot
            mt_tab, _ = _sel_try(page, ['a:has-text("Metrics")', 'button:has-text("Metrics")'])
            if mt_tab:
                mt_tab.click()
                page.wait_for_timeout(800)
                res["actions"].append("open_metrics_tab")
                txt = page.inner_text("body")
                for k in ["available", "unavailable", "preparing", "charging", "finishing"]:
                    res["metrics_snapshot"][k] = (k in txt.lower())

            # Users tab
            us_tab, _ = _sel_try(page, ['a:has-text("Users")', 'button:has-text("Users")'])
            if us_tab:
                us_tab.click()
                page.wait_for_timeout(700)
                res["actions"].append("open_users_tab")

            if cp.create_user:
                add_u_btn, _ = _sel_try(page, ['button:has-text("Add")', 'button:has-text("New")'])
                if add_u_btn:
                    add_u_btn.click()
                    page.wait_for_timeout(600)
                    res["actions"].append("create_user_open_form")

                user_fields = {
                    "name": cp.user_full_name,
                    "username": cp.user_username,
                    "password": cp.user_password,
                    "tag": cp.user_tag_id,
                    "company": cp.user_company,
                }
                for key, val in user_fields.items():
                    if not val:
                        continue
                    loc, _ = _sel_try(page, [f'input[name="{key}"]', f'input[id*="{key}"]'])
                    if loc:
                        loc.fill(str(val))
                    else:
                        res["warnings"].append(f"cpms_user_field_not_found:{key}")

                save_u_btn, _ = _sel_try(page, ['button:has-text("Save")', 'button:has-text("Create")'])
                if save_u_btn:
                    save_u_btn.click()
                    page.wait_for_timeout(900)
                    res["actions"].append("create_user_submit")
                else:
                    res["warnings"].append("cpms_user_save_not_found")

            # Settings tab snapshot
            st_tab, _ = _sel_try(page, ['a:has-text("Settings")', 'button:has-text("Settings")'])
            if st_tab:
                st_tab.click()
                page.wait_for_timeout(900)
                res["actions"].append("open_settings_tab")
                body_txt = page.inner_text("body").lower()
                res["settings_snapshot"] = {
                    "has_energy_section": "energy" in body_txt,
                    "has_connections_section": "connection" in body_txt,
                    "has_user_manager": "user manager" in body_txt,
                    "has_mdns": "mdns" in body_txt,
                }

            s2 = ev_dir / "99_final.png"
            page.screenshot(path=str(s2), full_page=True)
            res["evidence"]["screenshots"].append(str(s2))
            h2 = ev_dir / "99_final.html"
            h2.write_text(page.content(), encoding="utf-8")
            res["evidence"]["html"].append(str(h2))

        except Exception as e:
            res["errors"].append(f"cpms_runtime_error:{e}")
        finally:
            context.close()
            browser.close()

    res["finished_at"] = now_iso()
    res["ok"] = len(res["errors"]) == 0
    (out_dir / "cpms_phase" / "01_cpms_result.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return res


def run_unified(inp: UnifiedInput, out_base: Path) -> Dict[str, Any]:
    started = now_iso()
    errors = validate(inp)
    if errors:
        return {
            "version": VERSION,
            "status": "error",
            "error_code": "INVALID_INPUT",
            "errors": errors,
            "started_at": started,
            "ended_at": now_iso(),
        }

    run_dir = safe_mkdir(out_base, inp.run_id, inp.charger.ip)

    charger_result = run_charger_phase(inp, run_dir)
    cpms_result = run_cpms_phase(inp, run_dir)

    status = "ok" if charger_result.get("ok") and cpms_result.get("ok") else "error"

    out = {
        "version": VERSION,
        "status": status,
        "started_at": started,
        "ended_at": now_iso(),
        "run_id": inp.run_id,
        "artifacts": {
            "run_dir": str(run_dir),
            "charger_result": str(run_dir / "charger_phase" / "01_charger_result.json"),
            "cpms_result": str(run_dir / "cpms_phase" / "01_cpms_result.json"),
        },
        "charger_phase": {
            "ok": charger_result.get("ok"),
            "actions": charger_result.get("actions", []),
            "warnings": charger_result.get("warnings", []),
            "errors": charger_result.get("errors", []),
            "ocpp_before": charger_result.get("ocpp_before", {}),
            "ocpp_after": charger_result.get("ocpp_after", {}),
            "downloads": charger_result.get("evidence", {}).get("downloads", []),
        },
        "cpms_phase": {
            "ok": cpms_result.get("ok"),
            "actions": cpms_result.get("actions", []),
            "warnings": cpms_result.get("warnings", []),
            "errors": cpms_result.get("errors", []),
            "metrics_snapshot": cpms_result.get("metrics_snapshot", {}),
            "settings_snapshot": cpms_result.get("settings_snapshot", {}),
        },
    }

    (run_dir / "00_unified_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline unificado Webasto/Unite + CPMS con Playwright")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--out-base", default=str(DEFAULT_OUT_BASE))
    args = parser.parse_args()

    inp = load_input(Path(args.input))
    out = run_unified(inp, Path(args.out_base))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": out.get("status"), "output": str(out_path)}, ensure_ascii=False))
    return 0 if out.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
