from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class CpmsRunConfig:
    base_url: str
    username: str
    password: str
    expected_instance_ip: Optional[str] = None
    create_charger: bool = False
    charger_id: Optional[str] = None
    charger_name: Optional[str] = None
    connector_count: int = 1
    create_user: bool = False
    user_full_name: Optional[str] = None
    user_username: Optional[str] = None
    user_password: Optional[str] = None
    user_tag_id: Optional[str] = None
    user_company: Optional[str] = None
    user_role: str = "user"
    headless: bool = True
    timeout_ms: int = 25000


class CpmsPlaywrightExecutor:
    def __init__(self, config: CpmsRunConfig, out_dir: Path):
        self.config = config
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir = self.out_dir / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _sel_try(self, page, selectors: list[str]):
        for s in selectors:
            loc = page.locator(s).first
            if loc.count() > 0:
                return loc, s
        return None, None

    def run(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "started_at": self._now_iso(),
            "actions": [],
            "warnings": [],
            "errors": [],
            "evidence": {"screenshots": [], "html": []},
            "metrics_snapshot": {},
            "settings_snapshot": {},
        }

        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            res["errors"].append(f"playwright_import_error:{e}")
            res["finished_at"] = self._now_iso()
            res["ok"] = False
            return res

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.config.headless)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(self.config.timeout_ms)

            try:
                page.goto(self.config.base_url)
                user_loc, _ = self._sel_try(page, ['input[name="username"]', 'input[type="text"]'])
                pass_loc, _ = self._sel_try(page, ['input[name="password"]', 'input[type="password"]'])
                btn_loc, _ = self._sel_try(page, ['button[type="submit"]', 'input[type="submit"]', 'button:has-text("Login")'])
                if user_loc and pass_loc and btn_loc:
                    user_loc.fill(self.config.username)
                    pass_loc.fill(self.config.password)
                    btn_loc.click()
                    page.wait_for_timeout(1200)
                    res["actions"].append("cpms_login")
                else:
                    res["warnings"].append("cpms_login_selectors_partial")

                s1 = self.evidence_dir / "01_after_login.png"
                page.screenshot(path=str(s1), full_page=True)
                res["evidence"]["screenshots"].append(str(s1))
                h1 = self.evidence_dir / "01_after_login.html"
                h1.write_text(page.content(), encoding="utf-8")
                res["evidence"]["html"].append(str(h1))

                # Chargers
                ch_tab, _ = self._sel_try(page, ['a:has-text("Chargers")', 'button:has-text("Chargers")'])
                if ch_tab:
                    ch_tab.click(); page.wait_for_timeout(700)
                    res["actions"].append("open_chargers_tab")

                if self.config.create_charger:
                    add_btn, _ = self._sel_try(page, ['button:has-text("Add")', 'button:has-text("New")'])
                    if add_btn:
                        add_btn.click(); page.wait_for_timeout(600)
                        res["actions"].append("create_charger_open_form")
                    fields = {
                        "name": self.config.charger_name or f"CHG-{self.config.charger_id}",
                        "id": self.config.charger_id,
                        "connector": str(self.config.connector_count),
                    }
                    for key, val in fields.items():
                        if not val:
                            continue
                        loc, _ = self._sel_try(page, [f'input[name="{key}"]', f'input[id*="{key}"]'])
                        if loc:
                            loc.fill(val)
                        else:
                            res["warnings"].append(f"cpms_charger_field_not_found:{key}")
                    save_btn, _ = self._sel_try(page, ['button:has-text("Save")', 'button:has-text("Create")'])
                    if save_btn:
                        save_btn.click(); page.wait_for_timeout(900)
                        res["actions"].append("create_charger_submit")

                # Metrics snapshot
                mt_tab, _ = self._sel_try(page, ['a:has-text("Metrics")', 'button:has-text("Metrics")'])
                if mt_tab:
                    mt_tab.click(); page.wait_for_timeout(800)
                    res["actions"].append("open_metrics_tab")
                    txt = page.inner_text("body").lower()
                    for k in ["available", "unavailable", "preparing", "charging", "finishing"]:
                        res["metrics_snapshot"][k] = (k in txt)

                # Users
                us_tab, _ = self._sel_try(page, ['a:has-text("Users")', 'button:has-text("Users")'])
                if us_tab:
                    us_tab.click(); page.wait_for_timeout(700)
                    res["actions"].append("open_users_tab")

                if self.config.create_user:
                    add_u_btn, _ = self._sel_try(page, ['button:has-text("Add")', 'button:has-text("New")'])
                    if add_u_btn:
                        add_u_btn.click(); page.wait_for_timeout(600)
                        res["actions"].append("create_user_open_form")
                    u_fields = {
                        "name": self.config.user_full_name,
                        "username": self.config.user_username,
                        "password": self.config.user_password,
                        "tag": self.config.user_tag_id,
                        "company": self.config.user_company,
                    }
                    for key, val in u_fields.items():
                        if not val:
                            continue
                        loc, _ = self._sel_try(page, [f'input[name="{key}"]', f'input[id*="{key}"]'])
                        if loc:
                            loc.fill(str(val))
                        else:
                            res["warnings"].append(f"cpms_user_field_not_found:{key}")
                    save_u_btn, _ = self._sel_try(page, ['button:has-text("Save")', 'button:has-text("Create")'])
                    if save_u_btn:
                        save_u_btn.click(); page.wait_for_timeout(900)
                        res["actions"].append("create_user_submit")

                # Settings snapshot
                st_tab, _ = self._sel_try(page, ['a:has-text("Settings")', 'button:has-text("Settings")'])
                if st_tab:
                    st_tab.click(); page.wait_for_timeout(900)
                    res["actions"].append("open_settings_tab")
                    body_txt = page.inner_text("body").lower()
                    res["settings_snapshot"] = {
                        "has_energy_section": "energy" in body_txt,
                        "has_connections_section": "connection" in body_txt,
                        "has_user_manager": "user manager" in body_txt,
                        "has_mdns": "mdns" in body_txt,
                    }

                s2 = self.evidence_dir / "99_final.png"
                page.screenshot(path=str(s2), full_page=True)
                res["evidence"]["screenshots"].append(str(s2))
                h2 = self.evidence_dir / "99_final.html"
                h2.write_text(page.content(), encoding="utf-8")
                res["evidence"]["html"].append(str(h2))

            except Exception as e:
                res["errors"].append(f"cpms_runtime_error:{e}")
            finally:
                context.close(); browser.close()

        res["finished_at"] = self._now_iso()
        res["ok"] = len(res["errors"]) == 0
        return res


def run_cpms_playwright_session(config: CpmsRunConfig, out_dir: Path) -> Dict[str, Any]:
    return CpmsPlaywrightExecutor(config, out_dir).run()


def save_cpms_run_json(result: Dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path
