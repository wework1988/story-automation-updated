#!/usr/bin/env bash
# Convenience wrapper: loads repo-root .env (optional) then runs DeepSeek automation.
#
# Usage (from repo root):
#   ./crime-section/run_deepseek_pipeline.sh --story my-slug [--max-step 4]
#
# Example (stop after scene breakdown — no Stage C):
#   ./crime-section/run_deepseek_pipeline.sh --story madrid-haunting --max-step 3
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${ROOT}/.." && pwd)"

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/.env"
  set +a
fi

exec python3 "${ROOT}/helper/deepseek_pipeline.py" "$@"
