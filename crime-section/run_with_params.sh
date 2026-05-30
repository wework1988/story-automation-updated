#!/usr/bin/env bash
#
# ---------------------------------------------------------------------------
# crime-section/run_with_params.sh — DeepSeek automation (Steps 1 to 4)
# ---------------------------------------------------------------------------
#
# SIMPLE GUIDE (no coding skills needed)
#
#   • Put your Hindi/English episode text in THIS file:
#       crime-section/story-to-run/story.txt
#
#   • Scroll down to the box that says "*** EDIT HERE ***".
#     Edit only what is INSIDE the quote marks "...". Keep the quotes.
#
#   • Open Terminal on your Mac, go into THIS project folder
#       (the folder that contains crime-section), then type:
#
#       chmod +x crime-section/run_with_params.sh
#       ./crime-section/run_with_params.sh
#
#   • Had an error earlier? Set MY_OVERWRITE to "1" below, save, run again — or ask
#       someone to run:
#           STORY=my-name MAX_STEP=3 FORCE=1 ./crime-section/run_with_params.sh
#
#   • Default DeepSeek knobs (model, temps, searches, pipeline step, …): edit ONLY
#       crime-section/deepseek.config.example.ini
#     Nothing to copy—the script reads that file automatically. API keys still live in repo .env .
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
# Example: madrid-haunting
MY_FOLDER_NAME="spain-horror"

# One number only: 1, 2, 3, or 4 — how far automation should run
#
#   1 — Create folder & copy story (no AI)
#   2 — + build “story settings” (Stage A)
#   3 — + scene-by-scene plan (Stages A+B) — stops before picture prompts
#   4 — full run with picture-motion prompts too (Stages A+B+C — slowest/costliest)
MY_PIPELINE_STEP="4"

# "1" Redo AI steps even if files already exist (use after a failed run).
# "0" Normal runs — skip finished steps.
MY_OVERWRITE="1"

# ----- Optional extras (usual answer: leave as shown) -----

# If your script file is NOT story-to-run/story.txt — path from project root, or full path.
MY_CUSTOM_STORY_PATH="crime-section/story-to-run/story.txt"

# "1" Delete the whole stories/<MY_FOLDER_NAME> folder and start over (dangerous).
MY_DELETE_FOLDER_FIRST="0"

# "1" Use stories/<MY_FOLDER_NAME>/template/character.txt for fixed character looks.
MY_USE_FACE_LIBRARY="0"

# "1" Allow live internet inside DeepSeek (slower/noisier — usually "0").
MY_USE_INTERNET="0"

# Short hint for tone (example: paranormal documentary) — or leave empty.
MY_GENRE_HINT=""

# Only for step 4 — how many scenes per AI call (8 is a safe choice).
MY_SCENES_PER_BATCH="8"

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
#   STORY=slug FORCE=1 MAX_STEP=4 MODEL=deepseek-reasoner DEEPSEEK_TEMPERATURE=1 ./crime-section/run_with_params.sh
# Tip: tighten max tokens like the short API samples with e.g. export DEEPSEEK_MAX_TOKENS_C=16384
###############################################################

STORY="${STORY:-${MY_FOLDER_NAME}}"
MAX_STEP="${MAX_STEP:-${MY_PIPELINE_STEP}}"
FORCE="${FORCE:-${MY_OVERWRITE}}"

if [[ "${STORY}" == *"/"* || "${STORY}" == *..* ]]; then
  echo 'Error: MY_FOLDER_NAME must be simple (no "/" or ".."). Example: madrid-story'
  exit 1
fi

echo ""
echo "  Episode folder: ${STORY}"
echo "  Step to run:    ${MAX_STEP}  (see numbers 1–4 in the EDIT HERE box above)"
echo "  Overwrite:      ${FORCE}     (1 = redo AI even if output files exist)"
echo "  Default script: crime-section/story-to-run/story.txt"
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

exec python3 "${PIPELINE_PY}" "${args[@]}"
