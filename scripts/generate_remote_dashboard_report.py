#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reports.remote_report_dashboard_schema_v1 import RemoteDashboardReport
from reports.remote_report_dashboard_renderer_v1 import render_html, render_pdf_from_html


def main() -> int:
    p = argparse.ArgumentParser(description="Genera reporte dashboard remoto estricto (HTML + PDF)")
    p.add_argument("--data-json", required=True)
    p.add_argument("--output-html", required=True)
    p.add_argument("--output-pdf", required=True)
    args = p.parse_args()

    data = json.loads(Path(args.data_json).read_text(encoding="utf-8"))
    report = RemoteDashboardReport(**data)
    html = render_html(report, args.output_html)
    pdf = render_pdf_from_html(html, args.output_pdf)

    print(json.dumps({"ok": True, "html": html, "pdf": pdf}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
