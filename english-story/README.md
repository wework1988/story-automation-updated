# english-story — DeepSeek storyboard pipeline

Standalone package for **English-language** documentary / narrative episodes: **Stage A** (story config) → **Stage B** (scene breakdown) → **Stage C** (image + motion prompts).

Uses the shared engine in `crime-section/helper/deepseek_pipeline.py` (not modified). The launcher in `english-story/helper/deepseek_pipeline.py` points `--crime-root` here and loads **this** folder’s INI.

**Prompts:** Stage templates live in [`bifuracted-template/`](bifuracted-template/). Source draft for English rules: [`story-making-prompts/english-story/english-story-master`](../story-making-prompts/english-story/english-story-master) — copy or bifurcate into the three stage files when ready.

---

## Run a new episode (change story name only)

**Prerequisites:** Python 3, `pip install -r english-story/requirements-deepseek.txt`, repo-root `.env` with `DEEPSEEK_API_KEY`.

### 1. Put your script in `story-to-run/`

Either overwrite the default file or point to another path in step 2.

```text
english-story/story-to-run/story.txt          ← default
english-story/story-to-run/my-episode         ← example: custom filename
```

### 2. Edit `run_with_params.sh` — *** EDIT HERE *** block

Change **only** the quoted values. Minimal setup for a **full new episode**:

```bash
MY_FOLDER_NAME="my-english-episode"          # ← your slug (no spaces, no slashes)
MY_PIPELINE_STEP="4"                         # full run: config + breakdown + prompt.txt
MY_OVERWRITE="0"                             # "1" only to redo AI steps
MY_CUSTOM_STORY_PATH="english-story/story-to-run/story.txt"
MY_FILL_PROMPT_GAPS="0"                        # "1" only to patch missing scenes (see below)
```

| Variable | Typical value | Meaning |
|----------|---------------|---------|
| `MY_FOLDER_NAME` | `my-english-episode` | Creates / uses `stories/<slug>/` |
| `MY_PIPELINE_STEP` | `4` | `1` skeleton only · `2` +config · `3` +breakdown · `4` +prompts |
| `MY_OVERWRITE` | `0` | `1` = force API rerun even if outputs exist |
| `MY_CUSTOM_STORY_PATH` | path to your script | Synced into `stories/<slug>/FULL_STORY.txt` |
| `MY_FILL_PROMPT_GAPS` | `0` | `1` = fill missing scenes in existing `prompt.txt` only |

Optional: edit [`deepseek.config.example.ini`](deepseek.config.example.ini) for model, tokens, `scene_batch`, etc. API keys stay in repo `.env`, not the INI.

### 3. Run from repo root

```bash
chmod +x english-story/run_with_params.sh
./english-story/run_with_params.sh
```

**One-liner override** (no file edit — replace slug as needed):

```bash
STORY=my-english-episode MAX_STEP=4 ./english-story/run_with_params.sh
```

---

## What each pipeline step does

| Step | Command | Outputs |
|------|---------|---------|
| **1** | `MY_PIPELINE_STEP="1"` | `stories/<slug>/` skeleton + `FULL_STORY.txt` — **no LLM** |
| **2** | `MY_PIPELINE_STEP="2"` | `output_config_<slug>.md` |
| **3** | `MY_PIPELINE_STEP="3"` | `output_story_breakdown_<slug>.md` |
| **4** | `MY_PIPELINE_STEP="4"` | `prompt.txt` (batched Stage C API calls) |

After step 4 the pipeline also writes:

- `stories/<slug>/image-prompts-only.txt` — one IMAGE PROMPT per line
- `stories/<slug>/scene.txt` — scene headings + English narration lines

Slug must match everywhere: folder `stories/<slug>/` and filenames `output_*_<slug>.md`, `template/*_<slug>*`.

**Character library:** with `MY_USE_FACE_LIBRARY="1"`, the pipeline reads `stories/<slug>/template/character.txt`. Missing file → sends `NONE`.

---

## Layout

| Path | Role |
|------|------|
| [`bifuracted-template/`](bifuracted-template/) | Canonical Stage A/B/C specs — **update for English**; keep `PH_*` placeholders |
| [`stories/<slug>/`](stories/) | Per-episode outputs |
| [`story-to-run/`](story-to-run/) | Default script source before sync |
| [`deepseek.config.example.ini`](deepseek.config.example.ini) | Model, tokens, batch size, retries |
| [`run_with_params.sh`](run_with_params.sh) | **Main launcher** — edit `MY_*` then run |
| [`run_deepseek_pipeline.sh`](run_deepseek_pipeline.sh) | CLI wrapper (`--story`, `--max-step`, `--fill-prompt-gaps`) |
| [`helper/deepseek_pipeline.py`](helper/deepseek_pipeline.py) | Launcher → shared crime-section engine |
| [`PARITY.md`](PARITY.md) | Parity notes vs `crime-section/` and `general-story/` |
| [`helper/README.md`](helper/README.md) | Manual skeleton + optional Claude `auto_pipeline` |

---

## Customising templates

1. Edit or replace files in [`bifuracted-template/`](bifuracted-template/) from your English master prompt (`story-making-prompts/english-story/english-story-master`).
2. Keep placeholder strings compatible with the engine (`PH_*`, `PART 3 — INPUT SLOTS` in `crime-section/helper/deepseek_pipeline.py`).

---

## Relation to other packages

| Piece | Location |
|-------|----------|
| Shared DeepSeek implementation | `crime-section/helper/deepseek_pipeline.py` |
| Hindi / Hinglish general narratives | `general-story/` |
| English narratives | **Only** under `english-story/` |
