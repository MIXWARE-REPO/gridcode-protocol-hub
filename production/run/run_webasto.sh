#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-production/templates/webasto_input.template.json}"
OUTPUT="${2:-out/production_webasto_result.json}"

PYTHONPATH=. /home/laia/.venv/bin/python scripts/webasto_unite_strict_playwright.py \
  --input "$INPUT" \
  --output "$OUTPUT"

echo "OK -> $OUTPUT"
