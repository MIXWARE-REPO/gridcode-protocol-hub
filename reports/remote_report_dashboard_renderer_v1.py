from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from reports.remote_report_dashboard_schema_v1 import RemoteDashboardReport


def _env() -> Environment:
    templates_dir = Path(__file__).parent / "templates"
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_html(report: RemoteDashboardReport, output_html: str) -> str:
    ok, reason = report.validate()
    if not ok:
        raise ValueError(reason)

    tpl = _env().get_template("remote_dashboard_v1.html.j2")
    html = tpl.render(report=report)

    out = Path(output_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)


def render_pdf_from_html(html_path: str, output_pdf: str) -> str:
    from weasyprint import HTML

    out = Path(output_pdf)
    out.parent.mkdir(parents=True, exist_ok=True)
    HTML(filename=html_path).write_pdf(str(out))
    return str(out)
