from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ChargerRunConfig:
    ip: str
    username: str = "admin"
    password: str = ""
    target_endpoint: Optional[str] = None
    ocpp_updates: Optional[Dict[str, str]] = None
    download_logs: bool = True
    reboot: bool = False
    timeout_ms: int = 30000
    headless: bool = True
    allow_unsafe_actions: bool = False


class ChargerPlaywrightExecutor:
    def __init__(self, config: ChargerRunConfig, out_dir: Path):
        self.config = config
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir = self.out_dir / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _base_url(self) -> str:
        return f"http://{self.config.ip}"

    def _safe_filename(self, name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]", "_", name)

    def _save_text(self, name: str, content: str) -> str:
        p = self.evidence_dir / self._safe_filename(name)
        p.write_text(content, encoding="utf-8")
        return str(p)

    def _extract_ocpp_snapshot(self, html: str) -> Dict[str, Any]:
        endpoint = ""
        m = re.search(r'name=["\']centralSystemAddress["\'][^>]*value=["\']([^"\']*)["\']', html, re.I)
        if m:
            endpoint = m.group(1).strip()
        mode = None
        mode_m = re.search(r'name=["\']selectOCPPConnection["\'][^>]*>.*?<option[^>]*selected[^>]*value=["\']([^"\']+)', html, re.I | re.S)
        if mode_m:
            mode = mode_m.group(1)
        return {"centralSystemAddress": endpoint, "selectOCPPConnection": mode}

    def _build_result_base(self) -> Dict[str, Any]:
        return {
            "started_at": self._now_iso(),
            "ip": self.config.ip,
            "actions": [],
            "warnings": [],
            "errors": [],
            "evidence": {"screenshots": [], "html": [], "downloads": []},
            "ocpp_before": {},
            "ocpp_after": {},
        }

    def run(self) -> Dict[str, Any]:
        result = self._build_result_base()

        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            result["errors"].append(f"playwright_import_error: {e}")
            result["finished_at"] = self._now_iso()
            result["ok"] = False
            return result

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.config.headless)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(self.config.timeout_ms)

            try:
                # Login
                page.goto(self._base_url() + "/")
                page.fill('input[name="username"]', self.config.username)
                page.fill('input[name="pass"]', self.config.password)
                page.click('input[name="button_login"], button[name="button_login"], input[type="submit"]')
                page.wait_for_timeout(1000)
                result["actions"].append("login")

                login_shot = str(self.evidence_dir / "01_after_login.png")
                page.screenshot(path=login_shot, full_page=True)
                result["evidence"]["screenshots"].append(login_shot)

                html_main = page.content()
                html_path = self._save_text("01_main_after_login.html", html_main)
                result["evidence"]["html"].append(html_path)

                before_snapshot = self._extract_ocpp_snapshot(html_main)
                result["ocpp_before"] = before_snapshot

                # Update OCPP endpoint + variables
                if self.config.target_endpoint or self.config.ocpp_updates:
                    result["actions"].append("update_ocpp")

                    # Endpoint field
                    if self.config.target_endpoint:
                        endpoint_input = page.locator('input[name="centralSystemAddress"], #centralSystemAddress').first
                        endpoint_input.fill(self.config.target_endpoint)

                    # Arbitrary variable updates by name
                    for key, value in (self.config.ocpp_updates or {}).items():
                        loc = page.locator(f'[name="{key}"]').first
                        if loc.count() == 0:
                            result["warnings"].append(f"ocpp_var_not_found:{key}")
                            continue
                        tag = loc.evaluate("el => el.tagName.toLowerCase()")
                        if tag == "select":
                            loc.select_option(value=str(value))
                        else:
                            loc.fill(str(value))

                    # save
                    save_btn = page.locator('#ocpp_button, button[name="ocpp_button"], button:has-text("Save"), input[name="ocpp_button"]').first
                    save_btn.click()
                    page.wait_for_timeout(1500)

                # Read after
                html_after = page.content()
                after_path = self._save_text("02_main_after_update.html", html_after)
                result["evidence"]["html"].append(after_path)
                result["ocpp_after"] = self._extract_ocpp_snapshot(html_after)

                # Download logs
                if self.config.download_logs:
                    result["actions"].append("download_ocpp_logs")
                    with page.expect_download(timeout=self.config.timeout_ms) as download_info:
                        # preferred direct endpoint (works on UNITE when authenticated)
                        page.goto(self._base_url() + "/downloadOcppLogs.php")
                    download = download_info.value
                    suggested = download.suggested_filename or f"OCPP_logs_{self.config.ip}.zip"
                    logs_path = self.out_dir / self._safe_filename(suggested)
                    download.save_as(str(logs_path))
                    result["evidence"]["downloads"].append(str(logs_path))

                # Reboot (unsafe)
                if self.config.reboot:
                    if not self.config.allow_unsafe_actions:
                        result["warnings"].append("reboot_requested_but_blocked_without_allow_unsafe_actions")
                    else:
                        result["actions"].append("reboot")
                        reboot_btn = page.locator('button:has-text("Reboot"), input[value="Reboot"], #reboot_button').first
                        if reboot_btn.count() > 0:
                            reboot_btn.click()
                            page.wait_for_timeout(1500)
                        else:
                            result["warnings"].append("reboot_button_not_found")

                final_shot = str(self.evidence_dir / "99_final_state.png")
                page.screenshot(path=final_shot, full_page=True)
                result["evidence"]["screenshots"].append(final_shot)

            except Exception as e:
                result["errors"].append(f"runtime_error: {e}")
            finally:
                context.close()
                browser.close()

        result["finished_at"] = self._now_iso()
        result["ok"] = len(result["errors"]) == 0
        return result


def run_playwright_session(config: ChargerRunConfig, out_dir: Path) -> Dict[str, Any]:
    runner = ChargerPlaywrightExecutor(config=config, out_dir=out_dir)
    return runner.run()


def save_run_json(result: Dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path
