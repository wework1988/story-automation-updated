# Research story automation (crime-section pipeline)

This repository automates turning a **finished Hindi / Hinglish / English narrative script** into **per-scene image prompts and motion prompts** for 2D documentary-style animation (true crime, mystery, paranormal, etc.). The work happens in three **storyboard stages** (A → B → C), plus optional upstream story-writing templates.

You can run stages **manually in ChatGPT** (paste bifurcated templates) or **end-to-end via DeepSeek API** (recommended for repeat runs).

---

## What problem this solves

| Goal | What this repo produces |
|------|-------------------------|
| Lock era, geography, characters, and visual rules | **Stage A** → story config block |
| Split narration into ~5s beats with metadata | **Stage B** → locked scene breakdown |
| Ready-to-render prompts per scene | **Stage C** → `IMAGE PROMPT` + `DIGEN MOTION PROMPT` (batched) |

---

## Quick start (DeepSeek, all steps)

**Prerequisites**

- Python 3 with packages from [`crime-section/requirements-deepseek.txt`](crime-section/requirements-deepseek.txt) (`openai`, `python-dotenv`).
- Repo-root **`.env`** with `DEEPSEEK_API_KEY` (never commit real keys).

**1. Put your script in the inbox**

- Default path: [`crime-section/story-to-run/story.txt`](crime-section/story-to-run/story.txt)  
- Each pipeline run **syncs** this file into `crime-section/stories/<YOUR_SLUG>/FULL_STORY.txt`.

**2. Configure the runner**

- Edit [`crime-section/run_with_params.sh`](crime-section/run_with_params.sh) (`*** EDIT HERE ***`):  
  - `MY_FOLDER_NAME` — folder under `crime-section/stories/` (no spaces; use e.g. `my-episode`).  
  - `MY_PIPELINE_STEP` — `1` … `4` (see below).  
  - `MY_OVERWRITE` — `1` to redo AI steps when outputs already exist.

**3. Run from repo root**

```bash
chmod +x crime-section/run_with_params.sh
./crime-section/run_with_params.sh
```

Optional overrides (same script):

```bash
STORY=my-episode MAX_STEP=4 FORCE=1 ./crime-section/run_with_params.sh
```

**Pipeline steps (`--max-step` / `MY_PIPELINE_STEP`)**

| Step | Does |
|------|------|
| **1** | Ensures `stories/<slug>/` exists; copies bifurcated templates; syncs `FULL_STORY.txt` from `story-to-run/story.txt` — **no LLM** |
| **2** | Step 1 + **Stage A** (DeepSeek) → `output_config_<slug>.md` |
| **3** | Step 2 + **Stage B** → `output_story_breakdown_<slug>.md` |
| **4** | Step 3 + **Stage C** (batched) → `prompt.txt` |

Defaults and tuning (model, tokens, Stage B segments, batch size): [`crime-section/deepseek.config.example.ini`](crime-section/deepseek.config.example.ini).

Lower-level entrypoint (same Python backend):

```bash
./crime-section/run_deepseek_pipeline.sh --story my-episode --max-step 4
```

**Important:** The slug in **`MY_FOLDER_NAME` / `--story`** must match **every** artefact name in that folder — e.g. `output_config_<slug>.md`, `template/STORY_Config_<slug>.md`. If names drift (e.g. folder `spain-horror-2` but files say `spain-horror`), the pipeline will skip or write the wrong paths.

---

## Manual path (ChatGPT / no API)

Canonical instructions and slot-by-slot usage live here:

- [`crime-section/bifuracted-template/README.md`](crime-section/bifuracted-template/README.md)

Flow: paste **`stage-a`** → save config → paste **`stage-b`** → save breakdown → paste **`stage-c`** in batches with `SCENE_RANGE`.

---

## Repository layout (what each part is for)

### Root

| Path | Use |
|------|-----|
| `.env` | API keys (e.g. `DEEPSEEK_API_KEY`). **Do not commit secrets.** |

### `crime-section/` — main automation package

| Path | Use |
|------|-----|
| [`run_with_params.sh`](crime-section/run_with_params.sh) | Friendly wrapper: story slug, step 1–4, overwrite, optional paths → calls `helper/deepseek_pipeline.py`. |
| [`run_deepseek_pipeline.sh`](crime-section/run_deepseek_pipeline.sh) | Thin wrapper: loads `.env`, forwards CLI args to `deepseek_pipeline.py`. |
| [`deepseek.config.example.ini`](crime-section/deepseek.config.example.ini) | Non-secret defaults: model, `max_step`, token budgets, Stage B story segments, terminal UI, etc. |
| [`requirements-deepseek.txt`](crime-section/requirements-deepseek.txt) | Python deps for the DeepSeek pipeline. |
| [`story-to-run/story.txt`](crime-section/story-to-run/story.txt) | Default **source script** synced into each episode’s `FULL_STORY.txt` on every run. |

### `crime-section/bifuracted-template/` — golden templates (Stages A–C)

| File | Use |
|------|-----|
| `stage-a-story-config.md` | **Stage A** spec + slots: full story, optional genre, character library. |
| `stage-b-scene-breakdown.md` | **Stage B** spec + slots: story config block, full story, character library. |
| `stage-c-image-motion.md` | **Stage C** spec + slots: config, breakdown, character library, scene range. |
| `character.txt` | Example **locked character library** (verbatim blocks per `KEY`). Optional; pipeline can use per-story `template/character.txt`. |

Details: [`crime-section/bifuracted-template/README.md`](crime-section/bifuracted-template/README.md).

### `crime-section/stories/<slug>/` — one folder per episode

| File / folder | Use |
|---------------|-----|
| `FULL_STORY.txt` | Canonical script for this episode (overwritten from `story-to-run/story.txt` unless you change `--story-source`). |
| `output_config_<slug>.md` | **Stage A output** (story config block + structured metadata). Input to B and C. |
| `output_story_breakdown_<slug>.md` | **Stage B output** (numbered scenes, Hindi lines, metadata). Input to C. |
| `prompt.txt` | **Stage C output**: concatenated image + motion prompts for all batched scenes. |
| `template/` | Per-episode copies of A/B/C templates with **`_<slug>`** naming; mirrors get filled slots for debugging or manual paste. |
| `template/STORY_Config_<slug>.md` | Stage A mirror (filled story + library slots when automation runs). |
| `template/Story_scene_breakdown_<slug>.md` | Stage B mirror. |
| `template/<slug>_stage-c-image-motion.md` | Stage C mirror. |
| `template/character.txt` | Optional **episode-specific** locked faces/bodies; enable with `--use-character-lib` / INI `use_character_library`. |

### `crime-section/helper/` — scripts and backends

| Path | Use |
|------|-----|
| [`deepseek_pipeline.py`](crime-section/helper/deepseek_pipeline.py) | Full DeepSeek OpenAI-compatible client: sync story, Stage A/B/C, merging segmented Stage B, progress UI. |
| [`auto_pipeline.py`](crime-section/helper/auto_pipeline.py) | Claude / Anthropic automation path (see helper README). |
| [`create-story-skelton`](crime-section/helper/create-story-skelton) | Bash: create skeleton + optional template injection steps **without** LLM. |
| [`create-story-skelton-auto`](crime-section/helper/create-story-skelton-auto) | Runs A+B+C via Anthropic API with caching. |
| [`README.md`](crime-section/helper/README.md) | Skeleton script stages, placeholders, CLI overrides, auto mode env vars. |

### `crime-section/template/` — upstream narrative prompts

| Path | Use |
|------|-----|
| `story-writing`, `story-writing-master-prompt`, `title-thumbnailtext` | Prompts for **writing** or packaging episodes **before** the storyboard A→B→C pipeline. |

### `crime-section/library/`

Reference transcripts / samples (e.g. NoteGPT exports). **Not** consumed automatically by the DeepSeek runner unless you copy content into `story-to-run/story.txt` or a story folder.

---

## Alternative automation (Claude)

End-to-end Stage A+B+C via Anthropic is documented in [`crime-section/helper/README.md`](crime-section/helper/README.md) (`create-story-skelton-auto`, `ANTHROPIC_API_KEY`, batching, resume semantics).

---

## See also

- Bifurcated stage semantics, character library matching, crime sub-genre tables: [`crime-section/bifuracted-template/README.md`](crime-section/bifuracted-template/README.md)  
- Skeleton steps 1–4 and placeholders: [`crime-section/helper/README.md`](crime-section/helper/README.md)

---

## License / ops notes

- Treat API keys and private scripts as confidential.  
- Prefer **`FORCE=1`** only when you intend to **replace** existing `output_*` and regenerated `prompt.txt` segments (Stage C append behaviour is guarded — see `deepseek_pipeline.py`).
