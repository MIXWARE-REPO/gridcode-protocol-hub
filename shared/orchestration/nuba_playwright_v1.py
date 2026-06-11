from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class NubaRunConfig:
    base_url: str = "https://nuba.grid.touch"
    username: str = ""
    password: str = ""
    creator_filter: Optional[str] = None
    open_teleport_if_available: bool = False
    create_activation_code: bool = False
    activation_description: Optional[str] = None
    activation_product: Optional[str] = None
    activation_modules_csv: Optional[str] = None
    activation_expiry_date: Optional[str] = None
    headless: bool = True
    timeout_ms: int = 30000


class NubaPlaywrightExecutor:
    def __init__(self, config: NubaRunConfig, out_dir: Path):
        self.config = config
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir = out_dir / "evidence"
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
            "observations": {
                "clusters_detected": None,
                "nodes_detected": None,
                "dashboard_inactive_seen": False,
                "teleport_indicator_seen": False,
                "activation_code_generated": None,
            },
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
                page.wait_for_timeout(8000)

                u, _ = self._sel_try(page, ['input[name="email"]', 'input[name="username"]', 'input[type="email"]', 'input[type="text"]'])
                pw, _ = self._sel_try(page, ['input[name="password"]', 'input[type="password"]'])
                sb, _ = self._sel_try(page, ['button[type="submit"]', 'button:has-text("SUBMIT")', 'button:has-text("Login")', 'button:has-text("Sign in")', 'input[type="submit"]'])

                if u and pw and sb:
                    u.fill(self.config.username)
                    pw.fill(self.config.password)
                    sb.click()
                    page.wait_for_timeout(1600)
                    res["actions"].append("nuba_login")
                else:
                    res["errors"].append("nuba_login_selectors_not_found")

                s1 = self.evidence_dir / "01_after_login.png"
                page.screenshot(path=str(s1), full_page=True)
                res["evidence"]["screenshots"].append(str(s1))
                h1 = self.evidence_dir / "01_after_login.html"
                h1.write_text(page.content(), encoding="utf-8")
                res["evidence"]["html"].append(str(h1))

                # Open administration zone
                adm, _ = self._sel_try(page, ['a:has-text("Administration")', 'button:has-text("Administration")', 'a:has-text("Admin")'])
                if adm:
                    adm.click()
                    page.wait_for_timeout(900)
                    res["actions"].append("open_administration")
                else:
                    res["warnings"].append("administration_tab_not_found")

                # Optional filter by creator
                if self.config.creator_filter:
                    f_in, _ = self._sel_try(page, ['input[placeholder*="creator" i]', 'input[placeholder*="filter" i]', 'input[type="search"]'])
                    if f_in:
                        f_in.fill(self.config.creator_filter)
                        page.wait_for_timeout(700)
                        res["actions"].append("filter_by_creator")
                    else:
                        res["warnings"].append("creator_filter_input_not_found")

                page_text = page.inner_text("body").lower()
                res["observations"]["teleport_indicator_seen"] = ("teleport" in page_text or " teleport " in page_text)
                res["observations"]["dashboard_inactive_seen"] = ("dashboard inactive" in page_text or "inactivo" in page_text)
                res["observations"]["clusters_detected"] = ("cluster" in page_text)
                res["observations"]["nodes_detected"] = ("node" in page_text or "nodo" in page_text)

                # Teleport support quick open if requested
                if self.config.open_teleport_if_available:
                    tp, _ = self._sel_try(page, ['a:has-text("Teleport Support")', 'button:has-text("Teleport Support")'])
                    if tp:
                        tp.click()
                        page.wait_for_timeout(1200)
                        res["actions"].append("open_teleport_support")
                    else:
                        res["warnings"].append("teleport_support_not_found")

                # Licenses / activation codes
                lic, _ = self._sel_try(page, ['a:has-text("Licenses")', 'button:has-text("Licenses")', 'a:has-text("Activation")'])
                if lic:
                    lic.click()
                    page.wait_for_timeout(900)
                    res["actions"].append("open_licenses")

                    if self.config.create_activation_code:
                        add, _ = self._sel_try(page, [
                            'div.fixed.right-0.bottom-0.rounded-full.cursor-pointer',
                            'button:has-text("Add")',
                            'button:has-text("New")',
                            'button:has-text("Create")',
                            'button[aria-label="Add"]',
                            'button[aria-label="New"]',
                            'button[title="Add"]',
                            'button[title="New"]',
                            'button:has-text("+")',
                            'button.rounded-full',
                            'button.fixed.bottom-4.right-4',
                        ])
                        if add:
                            add.click(); page.wait_for_timeout(1200)
                            res["actions"].append("open_create_activation_code")
                        else:
                            res["warnings"].append("activation_plus_button_not_found")

                        d, _ = self._sel_try(page, [
                            'input[placeholder*="description" i]',
                            'textarea[placeholder*="description" i]',
                            'textarea[name="description"]',
                            'input[name="description"]',
                        ])
                        if d and self.config.activation_description:
                            d.fill(self.config.activation_description)

                        p_sel, _ = self._sel_try(page, ['select[name="product"]', 'select'])
                        if p_sel and self.config.activation_product:
                            try:
                                p_sel.select_option(label=self.config.activation_product)
                            except Exception:
                                try:
                                    p_sel.select_option(value=self.config.activation_product)
                                except Exception:
                                    res["warnings"].append("activation_product_select_failed")

                        m_in, _ = self._sel_try(page, ['input[name="modules"]', 'textarea[name="modules"]'])
                        if m_in and self.config.activation_modules_csv:
                            m_in.fill(self.config.activation_modules_csv)

                        ex, _ = self._sel_try(page, ['input[name="expiry"]', 'input[type="date"]'])
                        if ex and self.config.activation_expiry_date:
                            ex.fill(self.config.activation_expiry_date)

                        sv, _ = self._sel_try(page, ['button:has-text("SAVE")', 'button:has-text("Save")', 'button:has-text("Create")'])
                        if sv:
                            sv.click(); page.wait_for_timeout(1200)
                            res["actions"].append("create_activation_code_submit")
                        else:
                            res["warnings"].append("activation_save_button_not_found")

                        body = page.inner_text("body")
                        import re
                        m = re.search(r'(plus-[a-z0-9\-]{8,})', body, re.I)
                        if m:
                            res["observations"]["activation_code_generated"] = m.group(1)
                        else:
                            res["observations"]["activation_code_generated"] = "CODE" if "code" in body.lower() else None
                else:
                    res["warnings"].append("licenses_tab_not_found")

                sf = self.evidence_dir / "99_final.png"
                page.screenshot(path=str(sf), full_page=True)
                res["evidence"]["screenshots"].append(str(sf))
                hf = self.evidence_dir / "99_final.html"
                hf.write_text(page.content(), encoding="utf-8")
                res["evidence"]["html"].append(str(hf))

            except Exception as e:
                res["errors"].append(f"nuba_runtime_error:{e}")
            finally:
                context.close()
                browser.close()

        res["finished_at"] = self._now_iso()
        res["ok"] = len(res["errors"]) == 0
        return res


def run_nuba_playwright_session(config: NubaRunConfig, out_dir: Path) -> Dict[str, Any]:
    return NubaPlaywrightExecutor(config, out_dir).run()


def save_nuba_run_json(result: Dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path
