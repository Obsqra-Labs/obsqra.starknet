#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/backend/data"

SERIALIZER="${INTEGRITY_PROOF_SERIALIZER_BIN:-${ROOT_DIR}/integrity/target/release/proof_serializer}"
CAIRO0_PROOF="${ROOT_DIR}/integrity/examples/proofs/recursive/cairo0_stone5_keccak_160_lsb_example_proof.json"
CAIRO1_PROOF="${ROOT_DIR}/integrity/examples/proofs/recursive/cairo1_stone5_keccak_160_lsb_example_proof.json"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--serializer /path/to/proof_serializer] [--cairo0 /path/to/proof.json] [--cairo1 /path/to/proof.json]

Generates demo calldata files for the zkML verification UI:
  - backend/data/zkml_demo_cairo0.calldata
  - backend/data/zkml_demo_cairo1.calldata
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --serializer)
      SERIALIZER="$2"
      shift 2
      ;;
    --cairo0)
      CAIRO0_PROOF="$2"
      shift 2
      ;;
    --cairo1)
      CAIRO1_PROOF="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ ! -x "$SERIALIZER" ]]; then
  echo "proof_serializer not found, building it..."
  (cd "${ROOT_DIR}/integrity" && cargo build -p proof_serializer --release)
fi

if [[ ! -f "$CAIRO0_PROOF" ]]; then
  echo "Missing cairo0 proof JSON: $CAIRO0_PROOF"
  exit 1
fi

if [[ ! -f "$CAIRO1_PROOF" ]]; then
  echo "Missing cairo1 proof JSON: $CAIRO1_PROOF"
  exit 1
fi

mkdir -p "$OUT_DIR"

"$SERIALIZER" < "$CAIRO0_PROOF" > "${OUT_DIR}/zkml_demo_cairo0.calldata"
"$SERIALIZER" < "$CAIRO1_PROOF" > "${OUT_DIR}/zkml_demo_cairo1.calldata"

echo "✅ Wrote:"
echo "  ${OUT_DIR}/zkml_demo_cairo0.calldata"
echo "  ${OUT_DIR}/zkml_demo_cairo1.calldata"
