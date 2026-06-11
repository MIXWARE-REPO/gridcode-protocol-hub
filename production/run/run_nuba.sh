#!/usr/bin/env bash
set -euo pipefail

OUTPUT="${1:-out/production_nuba_result.json}"

PYTHONPATH=. /home/laia/.venv/bin/python scripts/run_nuba_playwright_v1.py \
  --base-url "https://nuba.grid-code.tech" \
  --username "${NUBA_USER:-REEMPLAZAR}" \
  --password "${NUBA_PASS:-REEMPLAZAR}" \
  --output "$OUTPUT"

echo "OK -> $OUTPUT"
