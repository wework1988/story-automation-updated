# general-story — DeepSeek storyboard pipeline

Standalone package for documentary / general narratives: **Stage A** (story config) → **Stage B** (scene breakdown) → **Stage C** (image + motion prompts).

Uses the shared engine in `crime-section/helper/deepseek_pipeline.py` (not modified). The launcher in `general-story/helper/deepseek_pipeline.py` points `--crime-root` here and loads **this** folder’s INI.

---

## Run a new episode (change story name only)

**Prerequisites:** Python 3, `pip install -r general-story/requirements-deepseek.txt`, repo-root `.env` with `DEEPSEEK_API_KEY`.

### 1. Put your script in `story-to-run/`

Either overwrite the default file or point to another path in step 2.

```text
general-story/story-to-run/story.txt          ← default
general-story/story-to-run/chardham           ← example: custom filename
```

### 2. Edit `run_with_params.sh` — *** EDIT HERE *** block

Change **only** the quoted values. Minimal setup for a **full new episode**:

```bash
MY_FOLDER_NAME="chardham"                    # ← your slug (no spaces, no slashes)
MY_PIPELINE_STEP="4"                         # full run: config + breakdown + prompt.txt
MY_OVERWRITE="0"                             # "1" only to redo AI steps
MY_CUSTOM_STORY_PATH="general-story/story-to-run/chardham"   # or story.txt
MY_FILL_PROMPT_GAPS="0"                        # "1" only to patch missing scenes (see below)
```

| Variable | Typical value | Meaning |
|----------|---------------|---------|
| `MY_FOLDER_NAME` | `chardham` | Creates / uses `stories/chardham/` |
| `MY_PIPELINE_STEP` | `4` | `1` skeleton only · `2` +config · `3` +breakdown · `4` +prompts |
| `MY_OVERWRITE` | `0` | `1` = force API rerun even if outputs exist |
| `MY_CUSTOM_STORY_PATH` | path to your script | Synced into `stories/<slug>/FULL_STORY.txt` |
| `MY_FILL_PROMPT_GAPS` | `0` | `1` = fill missing scenes in existing `prompt.txt` only |

Optional: edit [`deepseek.config.example.ini`](deepseek.config.example.ini) for model, tokens, `scene_batch`, etc. API keys stay in repo `.env`, not the INI.

### 3. Run from repo root

```bash
chmod +x general-story/run_with_params.sh
./general-story/run_with_params.sh
```

**One-liner override** (no file edit — replace `chardham` with your slug):

```bash
STORY=chardham MAX_STEP=4 ./general-story/run_with_params.sh
```

With a custom script path:

```bash
STORY=chardham MAX_STEP=4 ./general-story/run_with_params.sh
# and set MY_CUSTOM_STORY_PATH in the script, or:
python3 general-story/helper/deepseek_pipeline.py \
  --story chardham --max-step 4 \
  --story-source general-story/story-to-run/chardham
```

---

## Sample story: `yasin` (reference)

Use **`stories/yasin/`** as the worked example of a **complete** step‑4 run (~150 scenes, ~12 min per fill-gaps batch if needed).

| File | Description |
|------|-------------|
| [`stories/yasin/FULL_STORY.txt`](stories/yasin/FULL_STORY.txt) | Source script (synced from `story-to-run/`) |
| [`stories/yasin/output_config_yasin.md`](stories/yasin/output_config_yasin.md) | Stage A — era, characters, lighting, hostile profile |
| [`stories/yasin/output_story_breakdown_yasin.md`](stories/yasin/output_story_breakdown_yasin.md) | Stage B — locked scene list + Hindi lines |
| [`stories/yasin/prompt.txt`](stories/yasin/prompt.txt) | Stage C — `IMAGE PROMPT` + `DIGEN MOTION PROMPT` per scene |
| [`stories/yasin/template/character.txt`](stories/yasin/template/character.txt) | Optional CHARACTER_LIBRARY for Stages A/B/C |

To **reproduce the same settings** as the sample, keep defaults in `run_with_params.sh`:

```bash
MY_FOLDER_NAME="yasin"
MY_PIPELINE_STEP="4"
MY_CUSTOM_STORY_PATH="general-story/story-to-run/story.txt"   # or yasin.txt if you use that copy
```

---

## What each pipeline step does

| Step | Command | Outputs |
|------|---------|---------|
| **1** | `MY_PIPELINE_STEP="1"` | `stories/<slug>/` skeleton + `FULL_STORY.txt` — **no LLM** |
| **2** | `MY_PIPELINE_STEP="2"` | `output_config_<slug>.md` |
| **3** | `MY_PIPELINE_STEP="3"` | `output_story_breakdown_<slug>.md` |
| **4** | `MY_PIPELINE_STEP="4"` | `prompt.txt` (batched Stage C API calls) |

Slug must match everywhere: folder `stories/<slug>/` and filenames `output_*_<slug>.md`, `template/*_<slug>*`.

**Character library:** with `MY_USE_FACE_LIBRARY="1"`, the pipeline reads `stories/<slug>/template/character.txt`. Missing file → sends `NONE`.

---

## Stage C: missing scenes / fill gaps

If a full step‑4 run finishes but `prompt.txt` is **missing scene numbers** (thin API batch — often only ~4k chars instead of ~25k+ per batch):

1. **Do not** rerun all 150 scenes unless you want a full redo.
2. Set in `run_with_params.sh`:

```bash
MY_FOLDER_NAME="yasin"          # or your slug
MY_PIPELINE_STEP="4"
MY_OVERWRITE="0"
MY_FILL_PROMPT_GAPS="1"
```

3. Run `./general-story/run_with_params.sh` again.

The pipeline detects gaps vs Stage B, calls the API only for missing ranges, merges scenes in order, and rewrites `prompt.txt`.

**CLI equivalent:**

```bash
PIPELINE_STORY=yasin python3 general-story/helper/deepseek_pipeline.py \
  --story yasin --max-step 4 --fill-prompt-gaps --batch 4
```

New runs also **retry** short batches automatically (`stage_c_batch_retries` in INI).

---

## Layout

| Path | Role |
|------|------|
| [`bifuracted-template/`](bifuracted-template/) | Canonical Stage A/B/C specs — edit rules here; keep `PH_*` placeholders |
| [`stories/<slug>/`](stories/) | Per-episode outputs (see **yasin** sample) |
| [`story-to-run/`](story-to-run/) | Default script source before sync |
| [`deepseek.config.example.ini`](deepseek.config.example.ini) | Model, tokens, batch size, retries |
| [`run_with_params.sh`](run_with_params.sh) | **Main launcher** — edit `MY_*` then run |
| [`run_deepseek_pipeline.sh`](run_deepseek_pipeline.sh) | CLI wrapper (`--story`, `--max-step`, `--fill-prompt-gaps`) |
| [`helper/deepseek_pipeline.py`](helper/deepseek_pipeline.py) | Launcher → shared crime-section engine |
| [`PARITY.md`](PARITY.md) | Parity notes vs `crime-section/` |
| [`helper/README.md`](helper/README.md) | Manual skeleton + optional Claude `auto_pipeline` |

---

## Common recipes

**New episode from scratch**

```bash
# run_with_params.sh: MY_FOLDER_NAME="my-episode", MY_PIPELINE_STEP="4", MY_OVERWRITE="0"
./general-story/run_with_params.sh
```

**Redo breakdown only (keep config)**

```bash
STORY=my-episode MAX_STEP=3 FORCE=1 ./general-story/run_with_params.sh
```

**Redo full prompts**

```bash
STORY=my-episode MAX_STEP=4 FORCE=1 ./general-story/run_with_params.sh
```

**Patch missing prompts only**

```bash
# MY_FILL_PROMPT_GAPS="1", MY_OVERWRITE="0"
STORY=my-episode MAX_STEP=4 ./general-story/run_with_params.sh
```

**Cheaper / faster test (no Stage C)**

```bash
STORY=my-episode MAX_STEP=3 ./general-story/run_with_params.sh
```

---

## Troubleshooting

### `output_story_breakdown_<slug>.md` never appeared

Stage B did not finish. Check terminal for `[stage-b]` errors.

```bash
STORY=<slug> MAX_STEP=3 FORCE=1 ./general-story/run_with_params.sh
```

Raise `max_tokens_stage_b` or adjust `stage_b_story_segments` in [`deepseek.config.example.ini`](deepseek.config.example.ini) if you see `finish_reason=length`.

### Stage C stopped early / truncated

- Raise `max_tokens_stage_c` in INI.
- Lower `scene_batch` (e.g. `4`).
- Use `MY_FILL_PROMPT_GAPS="1"` to repair without a full rerun.

### `prompt.txt is non-empty — refusing to overwrite`

Either `MY_OVERWRITE="1"` for a full Stage C redo, or `MY_FILL_PROMPT_GAPS="1"` to add only missing scenes.

### Wrong INI defaults loaded

The launcher sets `DEEPSEEK_CONFIG_PATH` to `general-story/deepseek.config.example.ini`. Run via `./general-story/run_with_params.sh`, not the crime-section script without `--crime-root`.

---

## Customising templates

Edit [`bifuracted-template/`](bifuracted-template/) (`stage-a-story-config.md`, `stage-b-scene-breakdown.md`, `stage-c-image-motion.md`). Placeholder strings must stay compatible with the engine (`PH_*` in `crime-section/helper/deepseek_pipeline.py`).

---

## Relation to `crime-section/`

| Piece | Location |
|-------|----------|
| Shared DeepSeek implementation | `crime-section/helper/deepseek_pipeline.py` |
| Your specs & outputs | **Only** under `general-story/` |

---

## Optional: Claude automation

Anthropic A+B+C: see [`helper/README.md`](helper/README.md) (`create-story-skelton-auto`, `auto_pipeline.py`). Requires `ANTHROPIC_API_KEY` and `pip install -r requirements-claude.txt`.
