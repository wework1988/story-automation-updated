#!/usr/bin/env bash
#
# Create an isolated venv for elevenlabs-audio only.
# Avoids conflicts with tensorflow, torchcrepe, etc. in your global Python.
#
# Usage (from repo root):
#   ./elevenlabs-audio/setup.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${ROOT}/.venv"

if [[ ! -d "${VENV}" ]]; then
  echo "[setup] creating ${VENV}"
  python3 -m venv "${VENV}"
fi

# shellcheck source=/dev/null
source "${VENV}/bin/activate"

echo "[setup] installing requirements into isolated venv"
python -m pip install --upgrade pip
pip install -r "${ROOT}/requirements.txt"

echo "[setup] done — run: ./elevenlabs-audio/run.sh"
