
from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from reports.webasto_unite_log_report_schema_v1 import WebastoUniteLogReport


def _env() -> Environment:
    templates_dir = Path(__file__).parent / "templates"
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_html(report: WebastoUniteLogReport, output_html: str) -> str:
    ok, reason = report.validate()
    if not ok:
        raise ValueError(reason)

    tpl = _env().get_template("webasto_unite_log_report_v1.html.j2")
    html = tpl.render(report=report)

    out = Path(output_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)


def render_pdf_from_html(html_path: str, output_pdf: str) -> str:
    out = Path(output_pdf)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        from weasyprint import HTML  # type: ignore
        HTML(filename=html_path).write_pdf(str(out))
        return str(out)
    except Exception:
        from playwright.sync_api import sync_playwright
        html_file = Path(html_path).resolve()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(html_file.as_uri(), wait_until="load")
            page.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
            browser.close()
        return str(out)
