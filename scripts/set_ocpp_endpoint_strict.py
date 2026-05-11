#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(ip: str, password: str, endpoint: str, username: str = "admin", timeout_ms: int = 20000) -> dict:
    base = f"http://{ip}/"
    result = {
        "ip": ip,
        "target_endpoint": endpoint,
        "started_at": iso_now(),
        "status": "FAIL",
        "before_endpoint": None,
        "after_endpoint": None,
        "save_clicked": False,
        "save_disabled_after": None,
        "error": None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(ignore_https_errors=True)
        page = ctx.new_page()

        try:
            page.goto(base, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_selector('h1:has-text("LOGIN")', timeout=timeout_ms)
            page.fill('input[type="text"]', password)
            page.click('button:has-text("Login")')

            page.wait_for_selector('a:has-text("OCPP"), a:has-text("OCPP Settings")', timeout=timeout_ms)
            page.click('a:has-text("OCPP"), a:has-text("OCPP Settings")')

            endpoint_sel = 'input[value*="ws://"], input[name="centralSystemAddress"], input[type="text"]'
            page.wait_for_selector(endpoint_sel, timeout=timeout_ms)

            # pick the best input candidate: includes current ws/http endpoint
            candidates = page.locator('input')
            before = None
            endpoint_input = None
            for i in range(candidates.count()):
                v = (candidates.nth(i).input_value() or "").strip()
                if v.startswith("ws://") or v.startswith("wss://") or v.startswith("http://") or v.startswith("https://"):
                    before = v
                    endpoint_input = candidates.nth(i)
                    break

            if endpoint_input is None:
                raise RuntimeError("No se encontró campo de endpoint OCPP")

            result["before_endpoint"] = before
            endpoint_input.fill(endpoint)

            save_btn = page.locator('button:has-text("Save"), #ocpp_button').first
            save_btn.click(timeout=timeout_ms)
            result["save_clicked"] = True

            # allow async save + ui refresh
            page.wait_for_timeout(1500)

            # re-open OCPP to verify persisted value
            page.click('a:has-text("Dashboard")')
            page.wait_for_timeout(500)
            page.click('a:has-text("OCPP"), a:has-text("OCPP Settings")')
            page.wait_for_selector(endpoint_sel, timeout=timeout_ms)

            after = None
            candidates2 = page.locator('input')
            for i in range(candidates2.count()):
                v = (candidates2.nth(i).input_value() or "").strip()
                if v.startswith("ws://") or v.startswith("wss://") or v.startswith("http://") or v.startswith("https://"):
                    after = v
                    break
            result["after_endpoint"] = after

            # check save button disabled as extra signal
            try:
                result["save_disabled_after"] = save_btn.is_disabled()
            except Exception:
                result["save_disabled_after"] = None

            if after == endpoint:
                result["status"] = "OK"
            else:
                result["status"] = "FAIL"
                result["error"] = "Endpoint no persistió tras verificación"

        except PWTimeout as e:
            result["error"] = f"Timeout: {e}"
        except Exception as e:
            result["error"] = str(e)
        finally:
            result["finished_at"] = iso_now()
            ctx.close()
            browser.close()

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Cambio estricto de endpoint OCPP con verificación de persistencia")
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
