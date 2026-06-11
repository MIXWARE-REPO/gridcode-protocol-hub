#!/usr/bin/env python3
"""
Plantilla base para automatización web determinística con Playwright.

Objetivo:
- Input/Output contractuales
- Pasos explícitos y verificables
- Errores normalizados
- Evidencia mínima para auditoría

Uso:
  python3 shared/orchestration/web_automation_template_v1.py --input input.json --output out.json

Requiere:
  pip install playwright
  playwright install chromium
"""

from __future__ import annotations

import argparse
import json
import time
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from playwright.sync_api import Browser, BrowserContext, Error as PWError, Page, TimeoutError as PWTimeoutError, sync_playwright


VERSION = "web_automation_template_v1"


# =========================
# Contracts
# =========================

@dataclass
class StepDef:
    id: str
    action: str  # goto | click | type | wait_visible | assert_text | screenshot
    selector: Optional[str] = None
    value: Optional[str] = None
    timeout_ms: int = 10000
    retry: int = 0
    optional: bool = False


@dataclass
class BrowserConfig:
    headless: bool = True
    base_url: Optional[str] = None
    viewport_width: int = 1366
    viewport_height: int = 900
    navigation_timeout_ms: int = 30000
    action_timeout_ms: int = 10000


@dataclass
class AutomationInput:
    run_id: str
    target_url: str
    browser: BrowserConfig
    steps: list[StepDef]
    stop_on_error: bool = True
    capture_screenshots: bool = True


@dataclass
class StepResult:
    id: str
    status: str  # ok | error | skipped
    started_at: str
    ended_at: str
    duration_ms: int
    error_code: Optional[str] = None
    error_detail: Optional[str] = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationOutput:
    version: str
    status: str  # ok | error
    run_id: str
    started_at: str
    ended_at: str
    duration_ms: int
    final_url: Optional[str]
    steps_total: int
    steps_ok: int
    steps_error: int
    error_code: Optional[str]
    error_detail: Optional[str]
    step_results: list[StepResult]
    evidence: dict[str, Any]


# =========================
# Errors
# =========================

class ErrorCode:
    INVALID_INPUT = "INVALID_INPUT"
    NAVIGATION_FAILED = "NAVIGATION_FAILED"
    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"
    ACTION_TIMEOUT = "ACTION_TIMEOUT"
    ASSERTION_FAILED = "ASSERTION_FAILED"
    ACTION_FAILED = "ACTION_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# =========================
# Helpers
# =========================

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def elapsed_ms(t0: float) -> int:
    return int((time.monotonic() - t0) * 1000)


def read_input(path: Path) -> AutomationInput:
    raw = json.loads(path.read_text(encoding="utf-8"))

    if "run_id" not in raw or "target_url" not in raw or "steps" not in raw:
        raise ValueError("input debe incluir run_id, target_url y steps")

    browser_raw = raw.get("browser", {})
    browser = BrowserConfig(**browser_raw)

    steps = [StepDef(**s) for s in raw["steps"]]
    if not steps:
        raise ValueError("steps no puede estar vacío")

    return AutomationInput(
        run_id=raw["run_id"],
        target_url=raw["target_url"],
        browser=browser,
        steps=steps,
        stop_on_error=raw.get("stop_on_error", True),
        capture_screenshots=raw.get("capture_screenshots", True),
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def parse_step_error(exc: Exception) -> tuple[str, str]:
    msg = str(exc)
    if isinstance(exc, PWTimeoutError):
        return ErrorCode.ACTION_TIMEOUT, msg
    if "strict mode violation" in msg or "No node found" in msg:
        return ErrorCode.ELEMENT_NOT_FOUND, msg
    if isinstance(exc, AssertionError):
        return ErrorCode.ASSERTION_FAILED, msg
    if isinstance(exc, PWError):
        return ErrorCode.ACTION_FAILED, msg
    return ErrorCode.INTERNAL_ERROR, msg


# =========================
# Step actions
# =========================

def step_goto(page: Page, step: StepDef) -> dict[str, Any]:
    assert step.value, "goto requiere value con URL"
    page.goto(step.value, wait_until="domcontentloaded", timeout=step.timeout_ms)
    return {"url": page.url}


def step_click(page: Page, step: StepDef) -> dict[str, Any]:
    assert step.selector, "click requiere selector"
    page.locator(step.selector).first.click(timeout=step.timeout_ms)
    return {"selector": step.selector}


def step_type(page: Page, step: StepDef) -> dict[str, Any]:
    assert step.selector, "type requiere selector"
    assert step.value is not None, "type requiere value"
    loc = page.locator(step.selector).first
    loc.fill(step.value, timeout=step.timeout_ms)
    return {"selector": step.selector, "chars": len(step.value)}


def step_wait_visible(page: Page, step: StepDef) -> dict[str, Any]:
    assert step.selector, "wait_visible requiere selector"
    page.locator(step.selector).first.wait_for(state="visible", timeout=step.timeout_ms)
    return {"selector": step.selector}


def step_assert_text(page: Page, step: StepDef) -> dict[str, Any]:
    assert step.selector, "assert_text requiere selector"
    assert step.value is not None, "assert_text requiere value"
    text = page.locator(step.selector).first.inner_text(timeout=step.timeout_ms)
    if step.value not in text:
        raise AssertionError(f"Texto esperado '{step.value}' no encontrado en '{text}'")
    return {"selector": step.selector, "matched": step.value}


def step_screenshot(page: Page, step: StepDef, evidence_dir: Path) -> dict[str, Any]:
    filename = step.value or f"{step.id}.png"
    path = evidence_dir / filename
    page.screenshot(path=str(path), full_page=True)
    return {"screenshot": str(path)}


ACTION_MAP: dict[str, Callable[..., dict[str, Any]]] = {
    "goto": step_goto,
    "click": step_click,
    "type": step_type,
    "wait_visible": step_wait_visible,
    "assert_text": step_assert_text,
}


# =========================
# Runner
# =========================

def run_step(page: Page, step: StepDef, evidence_dir: Path, capture_screenshots: bool) -> StepResult:
    t0 = time.monotonic()
    started = now_iso()

    for attempt in range(step.retry + 1):
        try:
            if step.action == "screenshot":
                evidence = step_screenshot(page, step, evidence_dir)
            else:
                fn = ACTION_MAP.get(step.action)
                if not fn:
                    raise ValueError(f"action no soportada: {step.action}")
                evidence = fn(page, step)

            if capture_screenshots and step.action != "screenshot":
                auto_shot = evidence_dir / f"{step.id}.png"
                page.screenshot(path=str(auto_shot), full_page=False)
                evidence["auto_screenshot"] = str(auto_shot)

            ended = now_iso()
            return StepResult(
                id=step.id,
                status="ok",
                started_at=started,
                ended_at=ended,
                duration_ms=elapsed_ms(t0),
                evidence=evidence,
            )
        except Exception as exc:
            if attempt < step.retry:
                time.sleep(0.8)
                continue

            code, detail = parse_step_error(exc)
            ended = now_iso()

            if step.optional:
                return StepResult(
                    id=step.id,
                    status="skipped",
                    started_at=started,
                    ended_at=ended,
                    duration_ms=elapsed_ms(t0),
                    error_code=code,
                    error_detail=detail,
                )

            return StepResult(
                id=step.id,
                status="error",
                started_at=started,
                ended_at=ended,
                duration_ms=elapsed_ms(t0),
                error_code=code,
                error_detail=detail,
            )

    # unreachable
    ended = now_iso()
    return StepResult(
        id=step.id,
        status="error",
        started_at=started,
        ended_at=ended,
        duration_ms=elapsed_ms(t0),
        error_code=ErrorCode.INTERNAL_ERROR,
        error_detail="Estado inesperado",
    )


def run_automation(data: AutomationInput, output_path: Path, evidence_dir: Path) -> AutomationOutput:
    t0 = time.monotonic()
    started = now_iso()
    ensure_dir(evidence_dir)

    step_results: list[StepResult] = []
    final_url: Optional[str] = None
    global_error_code: Optional[str] = None
    global_error_detail: Optional[str] = None

    browser: Optional[Browser] = None
    context: Optional[BrowserContext] = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=data.browser.headless)
            context = browser.new_context(
                viewport={"width": data.browser.viewport_width, "height": data.browser.viewport_height}
            )
            page = context.new_page()
            page.set_default_navigation_timeout(data.browser.navigation_timeout_ms)
            page.set_default_timeout(data.browser.action_timeout_ms)

            # entrada principal al target
            page.goto(data.target_url, wait_until="domcontentloaded", timeout=data.browser.navigation_timeout_ms)

            for step in data.steps:
                res = run_step(page, step, evidence_dir=evidence_dir, capture_screenshots=data.capture_screenshots)
                step_results.append(res)

                if res.status == "error" and data.stop_on_error:
                    global_error_code = res.error_code
                    global_error_detail = res.error_detail
                    break

            final_url = page.url

    except Exception as exc:
        if not global_error_code:
            if isinstance(exc, PWTimeoutError):
                global_error_code = ErrorCode.NAVIGATION_FAILED
            else:
                global_error_code = ErrorCode.INTERNAL_ERROR
            global_error_detail = str(exc)
        # evidencia de stacktrace para debug interno
        (evidence_dir / "fatal_traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")

    finally:
        if context:
            context.close()
        if browser:
            browser.close()

    ended = now_iso()
    steps_ok = sum(1 for r in step_results if r.status == "ok")
    steps_error = sum(1 for r in step_results if r.status == "error")

    status = "ok" if steps_error == 0 and not global_error_code else "error"

    out = AutomationOutput(
        version=VERSION,
        status=status,
        run_id=data.run_id,
        started_at=started,
        ended_at=ended,
        duration_ms=elapsed_ms(t0),
        final_url=final_url,
        steps_total=len(data.steps),
        steps_ok=steps_ok,
        steps_error=steps_error,
        error_code=global_error_code,
        error_detail=global_error_detail,
        step_results=step_results,
        evidence={
            "evidence_dir": str(evidence_dir),
            "output_file": str(output_path),
        },
    )

    return out


def to_jsonable_output(out: AutomationOutput) -> dict[str, Any]:
    payload = asdict(out)
    payload["step_results"] = [asdict(s) for s in out.step_results]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Template determinístico de automatización web con Playwright")
    parser.add_argument("--input", required=True, help="Ruta a JSON de entrada")
    parser.add_argument("--output", required=True, help="Ruta a JSON de salida")
    parser.add_argument("--evidence-dir", default="out/web-evidence", help="Directorio de evidencia")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    evidence_dir = Path(args.evidence_dir)

    try:
        data = read_input(input_path)
    except Exception as exc:
        out = {
            "version": VERSION,
            "status": "error",
            "error_code": ErrorCode.INVALID_INPUT,
            "error_detail": str(exc),
            "step_results": [],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(out, ensure_ascii=False))
        return 2

    out_obj = run_automation(data, output_path=output_path, evidence_dir=evidence_dir)
    out_json = to_jsonable_output(out_obj)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out_json, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": out_obj.status, "output": str(output_path)}, ensure_ascii=False))

    return 0 if out_obj.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
