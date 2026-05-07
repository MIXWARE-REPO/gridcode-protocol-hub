#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reports.remote_report_strict_v1 import RemoteReportInput, build_strict_payload, render_pdf_from_template


def main() -> int:
    p = argparse.ArgumentParser(description="Genera reporte remoto estricto desde plantilla validada")
    p.add_argument("--template", required=True, help="Ruta PDF plantilla validada")
    p.add_argument("--output", required=True, help="Ruta PDF de salida")
    p.add_argument("--data-json", required=True, help="Ruta JSON con datos del caso")
    args = p.parse_args()

    data = json.loads(Path(args.data_json).read_text(encoding="utf-8"))
    model = RemoteReportInput(**data)
    payload = build_strict_payload(model)
    result = render_pdf_from_template(args.template, args.output, payload)

    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
