#!/usr/bin/env bash
# english-story — DeepSeek automation (delegates to crime-section/helper/deepseek_pipeline.py)
#
# Usage (from repo root):
#   ./english-story/run_deepseek_pipeline.sh --story my-slug [--max-step 4]
#
# Paths (templates, stories, INI) are always under english-story/ via --crime-root.
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
