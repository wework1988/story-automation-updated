#!/usr/bin/env bash
#
# elevenlabs-audio/run.sh — paste a story path, get MP3s
#
# Setup (once):
#   ./elevenlabs-audio/setup.sh
#   Add ELEVENLABS_API_KEY to repo-root .env
#
# Usage — paste your story path:
#   ./elevenlabs-audio/run.sh general-story/story-to-run/ic-427-final
#   ./elevenlabs-audio/run.sh /Users/you/project/my-story.txt
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${ROOT}/.." && pwd)"

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/.env"
  set +a
fi

###############################################################
#  *** PASTE YOUR STORY PATH HERE (or pass as argument) ***
###############################################################

MY_STORY_PATH="general-story/story-to-run/ic-427-final"

###############################################################

STORY_PATH="${1:-${STORY_PATH:-${MY_STORY_PATH}}}"

if [[ -z "${STORY_PATH}" ]]; then
  echo "Usage: ./elevenlabs-audio/run.sh <path-to-story-file-or-folder>" >&2
  echo "" >&2
  echo "Examples:" >&2
  echo "  ./elevenlabs-audio/run.sh general-story/story-to-run/ic-427-final" >&2
  echo "  ./elevenlabs-audio/run.sh elevenlabs-audio/input/test" >&2
  exit 1
fi

# Resolve relative paths from repo root
if [[ "${STORY_PATH}" != /* ]]; then
  STORY_PATH="${REPO_ROOT}/${STORY_PATH}"
fi

PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "${PYTHON}" ]]; then
  PYTHON="python3"
  echo "[elevenlabs] no local venv — run ./elevenlabs-audio/setup.sh first" >&2
fi

exec "${PYTHON}" "${ROOT}/generate_audio.py" "${STORY_PATH}" "${@:2}"
