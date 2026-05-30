#!/usr/bin/env bash
#
# ---------------------------------------------------------------------------
# general-story/run_with_params.sh — DeepSeek automation (Steps 1 to 4)
# ---------------------------------------------------------------------------
#
# SIMPLE GUIDE — see general-story/README.md (sample: stories/yasin/)
#
#   1. Put script in general-story/story-to-run/<your-file>
#   2. Below: set MY_FOLDER_NAME="your-slug" and MY_CUSTOM_STORY_PATH if not story.txt
#   3. From repo root: ./general-story/run_with_params.sh
#
#   Full run:     MY_PIPELINE_STEP="4"   MY_OVERWRITE="0"
#   Fix gaps:     MY_FILL_PROMPT_GAPS="1" (keeps existing prompt scenes)
#   Redo AI:      MY_OVERWRITE="1"
#
#   One-liner:  STORY=chardham MAX_STEP=4 ./general-story/run_with_params.sh
#
#   Model/tokens/batch: general-story/deepseek.config.example.ini
#   API key: repo .env → DEEPSEEK_API_KEY
#
# ---------------------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${ROOT}/.." && pwd)"
PIPELINE_PY="${ROOT}/helper/deepseek_pipeline.py"

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/.env"
  set +a
fi

###############################################################
#                  *** EDIT HERE ***
#    Only change the text INSIDE quote marks ("like this").
###############################################################

# Folder name for this episode (letters, digits, dashes OK — no spaces, no slashes).
# Example: my-doc-series-01
MY_FOLDER_NAME="amit-shah-migration-strategy"

# One number only: 1, 2, 3, or 4 — how far automation should run
#
#   1 — Create folder & copy story (no AI)
#   2 — + build “story settings” (Stage A)
#   3 — + scene-by-scene plan (Stages A+B) — stops before picture prompts
#   4 — full run with picture-motion prompts too (Stages A+B+C — slowest/costliest)
MY_PIPELINE_STEP="4"

# "1" Redo AI steps even if files already exist (use after a failed run).
# "0" Normal runs — skip finished steps.
MY_OVERWRITE="0"

# ----- Optional extras (usual answer: leave as shown) -----

# If your script file is NOT story-to-run/story.txt — path from project root, or full path.
MY_CUSTOM_STORY_PATH="general-story/story-to-run/story.txt"

# "1" Delete the whole stories/<MY_FOLDER_NAME> folder and start over (dangerous).
MY_DELETE_FOLDER_FIRST="0"

# "1" Use stories/<MY_FOLDER_NAME>/template/character.txt for fixed character looks (CHARACTER_LIBRARY).
# Default on so Stages A/B/C see your library when character.txt exists.
MY_USE_FACE_LIBRARY="1"

# "1" Allow live internet inside DeepSeek (slower/noisier — usually "0").
MY_USE_INTERNET="0"

# Short hint for tone (example: paranormal documentary) — or leave empty.
MY_GENRE_HINT=""

# Only for step 4 — how many scenes per AI call (8 is a safe choice).
MY_SCENES_PER_BATCH="8"

# Step 4 only — "1" fills missing scenes in prompt.txt (keeps existing scenes; no full redo).
MY_FILL_PROMPT_GAPS="0"

# Stage B only — print scene breakdown to terminal in chunks of N scenes (e.g. 10). 0 = one big paste.
MY_STAGE_B_TERMINAL_SCENES="10"

# Stage B — split FULL_STORY into N breakdown API calls then merge (empty = INI · e.g. 10 for long scripts · 0 = auto).
MY_STAGE_B_STORY_SEGMENTS=""

# DeepSeek model. Common picks:
#   deepseek-v4-pro     — flagship (recommended default)
#   deepseek-v4-flash   — faster / cheaper
#   deepseek-reasoner   — standalone reasoning (classic R1 path); many samples use DEEPSEEK_TEMPERATURE=1 with this
MY_MODEL_NAME="deepseek-v4-pro"

###############################################################
# Experts: export overrides before launch, for example:
#   STORY=slug FORCE=1 MAX_STEP=4 MODEL=deepseek-reasoner DEEPSEEK_TEMPERATURE=1 ./general-story/run_with_params.sh
# Tip: tighten max tokens like the short API samples with e.g. export DEEPSEEK_MAX_TOKENS_C=16384
###############################################################

STORY="${STORY:-${MY_FOLDER_NAME}}"
MAX_STEP="${MAX_STEP:-${MY_PIPELINE_STEP}}"
FORCE="${FORCE:-${MY_OVERWRITE}}"

if [[ "${STORY}" == *"/"* || "${STORY}" == *..* ]]; then
  echo 'Error: MY_FOLDER_NAME must be simple (no "/" or ".."). Example: my-doc-series-01'
  exit 1
fi

echo ""
echo "  Package:        general-story/"
echo "  Episode folder: ${STORY}"
echo "  Step to run:    ${MAX_STEP}  (see numbers 1–4 in the EDIT HERE box above)"
echo "  Overwrite:      ${FORCE}     (1 = redo AI even if output files exist)"
echo "  Default script: general-story/story-to-run/story.txt"
if [[ -n "${MY_CUSTOM_STORY_PATH}" ]]; then
  echo "  Custom script:  ${MY_CUSTOM_STORY_PATH}"
fi
echo ""

STORY_SOURCE="${MY_CUSTOM_STORY_PATH:-}"
RECREATE_STORY_DIR="${MY_DELETE_FOLDER_FIRST:-0}"
USE_CHARACTER_LIB="${MY_USE_FACE_LIBRARY:-0}"
WEB_SEARCH="${MY_USE_INTERNET:-0}"
GENRE="${MY_GENRE_HINT:-}"
BATCH="${MY_SCENES_PER_BATCH:-8}"
STAGE_B_TERMINAL_SCENES="${STAGE_B_TERMINAL_SCENES:-${MY_STAGE_B_TERMINAL_SCENES}}"
STAGE_B_STORY_SEGMENTS="${STAGE_B_STORY_SEGMENTS:-${MY_STAGE_B_STORY_SEGMENTS}}"
MODEL="${MODEL:-${MY_MODEL_NAME:-deepseek-v4-pro}}"

args=(--story "${STORY}" --max-step "${MAX_STEP}" --model "${MODEL}")

if [[ -n "${STORY_SOURCE}" ]]; then
  args+=(--story-source "${STORY_SOURCE}")
fi

if [[ "${FORCE}" == "1" ]]; then
  args+=(--force)
fi

if [[ "${RECREATE_STORY_DIR}" == "1" ]]; then
  args+=(--recreate-story-dir)
fi

if [[ "${USE_CHARACTER_LIB}" == "1" ]]; then
  args+=(--use-character-lib)
else
  args+=(--no-use-character-lib)
fi

if [[ "${WEB_SEARCH}" == "1" ]]; then
  args+=(--web-search)
fi

if [[ -n "${GENRE}" ]]; then
  args+=(--genre "${GENRE}")
fi

if [[ -n "${BATCH}" ]]; then
  args+=(--batch "${BATCH}")
fi

if [[ -n "${STAGE_B_TERMINAL_SCENES}" ]]; then
  args+=(--stage-b-terminal-scenes "${STAGE_B_TERMINAL_SCENES}")
fi

if [[ -n "${STAGE_B_STORY_SEGMENTS}" ]]; then
  args+=(--stage-b-story-segments "${STAGE_B_STORY_SEGMENTS}")
fi

if [[ "${MY_FILL_PROMPT_GAPS:-0}" == "1" ]]; then
  args+=(--fill-prompt-gaps)
fi

exec python3 "${PIPELINE_PY}" "${args[@]}"
