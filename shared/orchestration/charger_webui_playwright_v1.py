from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# SELECTORES FIJOS (UI estática Webasto/Unite)
# Nota: la UI real no expone snapshots ni APIs fiables para navegación;
# usamos selectores deterministas y visibles.
SEL_USERNAME = 'input[type="text"]'
SEL_PASSWORD = 'input[type="password"]'
SEL_LOGIN = 'input#button_login, input[type="submit"]#button_login, button#button_login'
SEL_BACKEND_MENU = 'button:has-text("Backend")'
SEL_OCPP_MENU = 'a:has-text("OCPP Settings")'
SEL_SYSTEM_MENU = 'a#systemNav, a:has-text("System Maintenance")'
SEL_GENERAL_TAB = 'a:has-text("General")'
SEL_DOWNLOAD_LOGS = 'button:has-text("Download Log Files")'
SEL_OCPP_LOG_BUTTON = '#ocpp_log_button'
SEL_HMI_LOG_BUTTON = '#hmi_log_button'
SEL_CENTRAL_SYSTEM = 'input[name="centralSystemAddress"]:visible, input#centralSystemAddress[name="centralSystemAddress"]:visible'
SEL_CHARGE_POINT_ID = 'input[name="chargePointId"]:visible, input#chargePointId[name="chargePointId"]:visible'
SEL_SAVE_OCPP = 'button:has-text("SAVE"):visible, button:has-text("Save"):visible'
SEL_FREE_MODE_ACTIVE = 'select#freeChargeModeActive[name="freeChargeModeActive"]'


@dataclass
class ChargerRunConfig:
    ip: str
    username: str = "admin"
    password: str = ""
    target_endpoint: Optional[str] = None
    ocpp_updates: Optional[Dict[str, str]] = None
    download_logs: bool = False
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
        return {"centralSystemAddress": endpoint}

    def _download_logs_archive(self, page, download_url: str, target_name: str) -> str:
        """Navigate to a log download endpoint and persist the resulting archive.

        Webasto Unite uses long-running generation before the browser receives the
        file. The UI may take several minutes, so this helper must tolerate long
        waits and treat `Download is starting` as a successful transition.
        """
        with page.expect_download(timeout=self.config.timeout_ms) as download_info:
            try:
                page.goto(download_url, wait_until="load", timeout=self.config.timeout_ms)
            except Exception as e:
                if "Download is starting" not in str(e):
                    raise
        download = download_info.value
        target = self.evidence_dir / self._safe_filename(target_name)
        download.save_as(str(target))
        return str(target)

    def _login(self, page) -> None:
        page.goto(self._base_url() + "/", wait_until="domcontentloaded")
        page.wait_for_selector(SEL_USERNAME, state="visible", timeout=self.config.timeout_ms)
        page.locator(SEL_USERNAME).first.fill(self.config.username)
        page.wait_for_selector(SEL_PASSWORD, state="visible", timeout=self.config.timeout_ms)
        page.locator(SEL_PASSWORD).first.fill(self.config.password)
        page.locator(SEL_LOGIN).first.click(timeout=self.config.timeout_ms)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

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
            result["errors"].append(f"playwright_import_error:{e}")
            result["finished_at"] = self._now_iso()
            result["ok"] = False
            return result

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.config.headless)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(self.config.timeout_ms)

            try:
                # 1) Login
                self._login(page)
                result["actions"].append("login")

                # 2) Ir a OCPP Settings si todavía no está visible
                if page.locator(SEL_CENTRAL_SYSTEM).count() == 0:
                    if page.locator('a#ocppNav').count() > 0:
                        page.click('a#ocppNav')
                        page.wait_for_timeout(700)
                        result["actions"].append("open_ocpp_settings_tab")
                    elif page.locator(SEL_OCPP_MENU).count() > 0:
                        page.click(SEL_OCPP_MENU)
                        page.wait_for_timeout(700)
                        result["actions"].append("open_ocpp_settings")
                    elif page.locator(SEL_BACKEND_MENU).count() > 0:
                        page.click(SEL_BACKEND_MENU)
                        page.wait_for_timeout(700)
                        result["actions"].append("open_backend_menu")

                if page.locator(SEL_CENTRAL_SYSTEM).count() == 0:
                    html = page.content()
                    if "User authentication failed" in html:
                        result["errors"].append("auth_failed")
                    else:
                        result["errors"].append("post_login_ocpp_menu_not_found")
                    return result

                # 3) Snapshot before
                html_before = page.content()
                result["ocpp_before"] = self._extract_ocpp_snapshot(html_before)
                result["evidence"]["html"].append(self._save_text("01_ocpp_before.html", html_before))

                # 4) Update endpoint
                if self.config.target_endpoint:
                    page.locator(SEL_CENTRAL_SYSTEM).first.fill(self.config.target_endpoint)

                # 5) Update vars (solo select/text existentes)
                for key, value in (self.config.ocpp_updates or {}).items():
                    loc = page.locator(f'[name="{key}"]')
                    if loc.count() == 0:
                        result["warnings"].append(f"ocpp_var_not_found:{key}")
                        continue
                    tag = loc.first.evaluate("el => el.tagName.toLowerCase()")
                    if tag == "select":
                        loc.first.select_option(value=str(value))
                    else:
                        loc.first.fill(str(value))

                # 6) Save
                page.locator(SEL_SAVE_OCPP).first.click(timeout=self.config.timeout_ms)
                page.wait_for_timeout(1200)
                result["actions"].append("save_ocpp")

                # 7) Relectura persistida (ir Main y volver a OCPP)
                page.locator('a:has-text("Main Page")').first.click(timeout=self.config.timeout_ms)
                page.wait_for_timeout(500)
                if page.locator('a#ocppNav').count() > 0:
                    page.locator('a#ocppNav').first.click(timeout=self.config.timeout_ms)
                else:
                    page.locator(SEL_OCPP_MENU).first.click(timeout=self.config.timeout_ms)
                page.wait_for_timeout(700)
                result["actions"].append("reopen_ocpp_for_persistence_check")

                html_after = page.content()
                result["ocpp_after"] = self._extract_ocpp_snapshot(html_after)
                result["evidence"]["html"].append(self._save_text("02_ocpp_after.html", html_after))

                s = str(self.evidence_dir / "99_final_state.png")
                page.screenshot(path=s, full_page=True)
                result["evidence"]["screenshots"].append(s)

                if self.config.download_logs:
                    page.evaluate("document.body.style.zoom='50%'")
                    page.locator(SEL_SYSTEM_MENU).first.click(timeout=self.config.timeout_ms)
                    page.wait_for_timeout(700)
                    if page.locator(SEL_GENERAL_TAB).count() > 0:
                        page.locator(SEL_GENERAL_TAB).first.click(timeout=self.config.timeout_ms)
                        page.wait_for_timeout(500)
                    downloaded = self._download_logs_archive(
                        page,
                        f"{self._base_url()}/downloadOcppLogs.php",
                        "OCPP_logs.zip",
                    )
                    result["evidence"]["downloads"].append(downloaded)
                    result["actions"].append("download_ocpp_logs")

                if self.config.target_endpoint and result["ocpp_after"].get("centralSystemAddress") != self.config.target_endpoint:
                    result["errors"].append("persistence_check_failed_endpoint_mismatch")

            except Exception as e:
                result["errors"].append(f"runtime_error:{e}")
            finally:
                context.close()
                browser.close()

        result["finished_at"] = self._now_iso()
        result["ok"] = len(result["errors"]) == 0
        return result


def run_playwright_session(config: ChargerRunConfig, out_dir: Path) -> Dict[str, Any]:
    return ChargerPlaywrightExecutor(config=config, out_dir=out_dir).run()


def save_run_json(result: Dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path
