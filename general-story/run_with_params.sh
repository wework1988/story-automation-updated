#!/usr/bin/env bash
#
# ---------------------------------------------------------------------------
# general-story/run_with_params.sh — DeepSeek automation (Steps 1 to 4)
# ---------------------------------------------------------------------------
#
# After Step 4 (every run, even when Stage C is skipped because prompt.txt exists):
#   stories/<slug>/image-prompts-only.txt  — one IMAGE PROMPT per line
#   stories/<slug>/scene.txt               — scene headings + Hindi lines only
#   stories/<slug>/eleven-labs/            — narration MP3s (if MY_RUN_ELEVENLABS="1")
#
# SIMPLE GUIDE — see general-story/README.md (sample: stories/yasin/)
#
#   ONE story:  edit MY_FOLDER_NAME + MY_CUSTOM_STORY_PATH below (or leave queue.txt empty)
#   MANY stories: list them in general-story/story-to-run/queue.txt (one per line)
#   1. Put scripts in general-story/story-to-run/<your-file>
#   2. From repo root: ./general-story/run_with_params.sh
#
#   Full run:     MY_PIPELINE_STEP="4"   MY_OVERWRITE="0"
#   Fix gaps:     MY_FILL_PROMPT_GAPS="1" (keeps existing prompt scenes)
#   Redo AI:      MY_OVERWRITE="1"
#
#   One-liner:  STORY=chardham MAX_STEP=4 ./general-story/run_with_params.sh
#
#   Model/tokens/batch: general-story/deepseek.config.example.ini
#   API keys: repo .env → DEEPSEEK_API_KEY, ELEVENLABS_API_KEY
#   ElevenLabs setup: ./elevenlabs-audio/setup.sh
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
MY_FOLDER_NAME="cockroach"

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
# Used for single-story runs only (when queue.txt is missing or has no active lines).
MY_CUSTOM_STORY_PATH="general-story/story-to-run/story.txt"

# Batch queue: slug|story-path per line. Empty or missing file → single-story mode above.
MY_QUEUE_FILE="general-story/story-to-run/queue.txt"

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

# After step 4 finishes — generate narration MP3s from FULL_STORY.txt into
# stories/<slug>/eleven-labs/  ("0" to skip)
MY_RUN_ELEVENLABS="1"

###############################################################
# Experts: export overrides before launch, for example:
#   STORY=slug FORCE=1 MAX_STEP=4 MODEL=deepseek-reasoner DEEPSEEK_TEMPERATURE=1 ./general-story/run_with_params.sh
#   RUN_ELEVENLABS=0 ./general-story/run_with_params.sh   # skip narration MP3s
# Tip: tighten max tokens like the short API samples with e.g. export DEEPSEEK_MAX_TOKENS_C=16384
###############################################################

STORY="${STORY:-${MY_FOLDER_NAME}}"
MAX_STEP="${MAX_STEP:-${MY_PIPELINE_STEP}}"
FORCE="${FORCE:-${MY_OVERWRITE}}"

validate_story_slug() {
  local slug="$1"
  if [[ "${slug}" == *"/"* || "${slug}" == *..* ]]; then
    echo "Error: story slug must be simple (no \"/\" or \"..\"). Got: ${slug}"
    exit 1
  fi
}

RECREATE_STORY_DIR="${MY_DELETE_FOLDER_FIRST:-0}"
USE_CHARACTER_LIB="${MY_USE_FACE_LIBRARY:-0}"
WEB_SEARCH="${MY_USE_INTERNET:-0}"
GENRE="${MY_GENRE_HINT:-}"
BATCH="${MY_SCENES_PER_BATCH:-8}"
STAGE_B_TERMINAL_SCENES="${STAGE_B_TERMINAL_SCENES:-${MY_STAGE_B_TERMINAL_SCENES}}"
STAGE_B_STORY_SEGMENTS="${STAGE_B_STORY_SEGMENTS:-${MY_STAGE_B_STORY_SEGMENTS}}"
MODEL="${MODEL:-${MY_MODEL_NAME:-deepseek-v4-pro}}"

build_pipeline_args() {
  local story="$1"
  local story_source="$2"

  PIPELINE_ARGS=(--story "${story}" --max-step "${MAX_STEP}" --model "${MODEL}")

  if [[ -n "${story_source}" ]]; then
    PIPELINE_ARGS+=(--story-source "${story_source}")
  fi

  if [[ "${FORCE}" == "1" ]]; then
    PIPELINE_ARGS+=(--force)
  fi

  if [[ "${RECREATE_STORY_DIR}" == "1" ]]; then
    PIPELINE_ARGS+=(--recreate-story-dir)
  fi

  if [[ "${USE_CHARACTER_LIB}" == "1" ]]; then
    PIPELINE_ARGS+=(--use-character-lib)
  else
    PIPELINE_ARGS+=(--no-use-character-lib)
  fi

  if [[ "${WEB_SEARCH}" == "1" ]]; then
    PIPELINE_ARGS+=(--web-search)
  fi

  if [[ -n "${GENRE}" ]]; then
    PIPELINE_ARGS+=(--genre "${GENRE}")
  fi

  if [[ -n "${BATCH}" ]]; then
    PIPELINE_ARGS+=(--batch "${BATCH}")
  fi

  if [[ -n "${STAGE_B_TERMINAL_SCENES}" ]]; then
    PIPELINE_ARGS+=(--stage-b-terminal-scenes "${STAGE_B_TERMINAL_SCENES}")
  fi

  if [[ -n "${STAGE_B_STORY_SEGMENTS}" ]]; then
    PIPELINE_ARGS+=(--stage-b-story-segments "${STAGE_B_STORY_SEGMENTS}")
  fi

  if [[ "${MY_FILL_PROMPT_GAPS:-0}" == "1" ]]; then
    PIPELINE_ARGS+=(--fill-prompt-gaps)
  fi
}

run_elevenlabs_audio() {
  local story="$1"
  local story_dir="${ROOT}/stories/${story}"
  local full_story="${story_dir}/FULL_STORY.txt"
  local audio_out="${story_dir}/eleven-labs"
  local eleven_py="${REPO_ROOT}/elevenlabs-audio/generate_audio.py"
  local python="${REPO_ROOT}/elevenlabs-audio/.venv/bin/python"

  if [[ "${RUN_ELEVENLABS:-${MY_RUN_ELEVENLABS:-0}}" != "1" ]]; then
    return 0
  fi

  if [[ "${MAX_STEP}" -lt 4 ]]; then
    return 0
  fi

  if [[ ! -f "${full_story}" ]]; then
    echo "[elevenlabs] skipped — no FULL_STORY.txt in ${story_dir}"
    return 0
  fi

  if [[ ! -x "${python}" ]]; then
    echo "[elevenlabs] error — run ./elevenlabs-audio/setup.sh first"
    return 1
  fi

  echo ""
  echo "  ElevenLabs audio: ${full_story}"
  echo "  Output folder:    ${audio_out}/"
  echo ""

  "${python}" "${eleven_py}" "${full_story}" --output-dir "${audio_out}"
}

run_one_story() {
  local story="$1"
  local story_source="$2"

  validate_story_slug "${story}"
  build_pipeline_args "${story}" "${story_source}"

  echo ""
  echo "  Package:        general-story/"
  echo "  Episode folder: ${story}"
  echo "  Step to run:    ${MAX_STEP}  (see numbers 1–4 in the EDIT HERE box above)"
  echo "  Overwrite:      ${FORCE}     (1 = redo AI even if output files exist)"
  if [[ "${RUN_ELEVENLABS:-${MY_RUN_ELEVENLABS:-0}}" == "1" && "${MAX_STEP}" -ge 4 ]]; then
    echo "  ElevenLabs:     1  (MP3s → stories/${story}/eleven-labs/)"
  fi
  if [[ -n "${story_source}" ]]; then
    echo "  Story script:   ${story_source}"
  else
    echo "  Story script:   general-story/story-to-run/story.txt (default)"
  fi
  echo ""

  python3 "${PIPELINE_PY}" "${PIPELINE_ARGS[@]}"
  run_elevenlabs_audio "${story}"
}

load_queue_entries() {
  local queue_path="$1"
  local line slug source

  QUEUE_ENTRIES=()
  [[ -f "${queue_path}" ]] || return 0

  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "${line}" ]] && continue

    if [[ "${line}" != *"|"* ]]; then
      echo "Error: invalid queue line (expected slug|path): ${line}"
      echo "  File: ${queue_path}"
      exit 1
    fi

    slug="${line%%|*}"
    source="${line#*|}"
    slug="${slug#"${slug%%[![:space:]]*}"}"
    slug="${slug%"${slug##*[![:space:]]}"}"
    source="${source#"${source%%[![:space:]]*}"}"
    source="${source%"${source##*[![:space:]]}"}"

    if [[ -z "${slug}" || -z "${source}" ]]; then
      echo "Error: queue line needs slug and path: ${line}"
      echo "  File: ${queue_path}"
      exit 1
    fi

    QUEUE_ENTRIES+=("${slug}|${source}")
  done < "${queue_path}"
}

QUEUE_FILE="${QUEUE_FILE:-${MY_QUEUE_FILE:-general-story/story-to-run/queue.txt}}"
if [[ "${QUEUE_FILE}" == /* ]]; then
  QUEUE_PATH="${QUEUE_FILE}"
else
  QUEUE_PATH="${REPO_ROOT}/${QUEUE_FILE}"
fi

load_queue_entries "${QUEUE_PATH}"

if [[ ${#QUEUE_ENTRIES[@]} -gt 0 ]]; then
  total=${#QUEUE_ENTRIES[@]}
  echo ""
  echo "  Batch mode:     ${total} stor$( [[ "${total}" == 1 ]] && echo y || echo ies ) from ${QUEUE_FILE}"
  echo "  Step to run:    ${MAX_STEP}"
  echo "  Overwrite:      ${FORCE}"
  echo ""

  idx=0
  for entry in "${QUEUE_ENTRIES[@]}"; do
    idx=$((idx + 1))
    story_slug="${entry%%|*}"
    story_source="${entry#*|}"

    echo "================================================================"
    echo "  Story ${idx}/${total}: ${story_slug}"
    echo "================================================================"

    run_one_story "${story_slug}" "${story_source}"
  done

  echo ""
  echo "  Batch complete: ${total} stor$( [[ "${total}" == 1 ]] && echo y || echo ies ) finished."
  echo ""
  exit 0
fi

# Single-story fallback (MY_FOLDER_NAME + MY_CUSTOM_STORY_PATH)
run_one_story "${STORY}" "${MY_CUSTOM_STORY_PATH:-}"
