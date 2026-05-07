from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from reports.aggregated_report_strict_v2_schema import AggregatedReportV2


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_html(report: AggregatedReportV2, out_html: str) -> str:
    ok, reason = report.validate()
    if not ok:
        raise ValueError(reason)
    html = _env().get_template("aggregated_report_strict_v2.html.j2").render(r=report)
    p = Path(out_html)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    return str(p)


def render_pdf(out_html: str, out_pdf: str) -> str:
    from weasyprint import HTML

    p = Path(out_pdf)
    p.parent.mkdir(parents=True, exist_ok=True)
    HTML(filename=out_html).write_pdf(str(p))
    return str(p)
