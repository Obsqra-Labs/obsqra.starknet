#!/usr/bin/env bash
# Quick Stage 3A API check. Expects backend running on port 8001 (or set BASE_URL).
# Usage: ./scripts/verify_stage3a_api.sh

set -e
BASE_URL="${BASE_URL:-http://localhost:8001}"
ENDPOINT="${BASE_URL}/api/v1/risk-engine/model-params/0"

echo "Stage 3A API check: GET $ENDPOINT"
if ! curl -sf "$ENDPOINT" > /tmp/stage3a_response.json; then
  echo "FAIL: Could not reach backend (is it running? use: cd backend && python3 -m uvicorn main:app --port 8001)"
  exit 1
fi

# Expect JSON with at least w_utilization, clamp_min, clamp_max
if ! jq -e '.w_utilization, .clamp_min, .clamp_max' /tmp/stage3a_response.json > /dev/null 2>&1; then
  echo "FAIL: Response missing expected keys (w_utilization, clamp_min, clamp_max)"
  cat /tmp/stage3a_response.json
  exit 1
fi

echo "OK: Model params returned"
jq '.' /tmp/stage3a_response.json
