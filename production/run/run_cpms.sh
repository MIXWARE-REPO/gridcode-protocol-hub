#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-production/templates/cpms_input.template.json}"
OUTPUT="${2:-out/production_cpms_result.json}"

PYTHONPATH=. /home/laia/.venv/bin/python scripts/cpms_wings_create_charger.py \
  --input "$INPUT" \
  --output "$OUTPUT"

echo "OK -> $OUTPUT"
