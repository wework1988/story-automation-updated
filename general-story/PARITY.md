# Feature parity: `general-story/` vs `crime-section/`

Both packages run the **same** DeepSeek engine: `crime-section/helper/deepseek_pipeline.py`. General-story **does not** fork that file; `general-story/helper/deepseek_pipeline.py` is a launcher that sets `DEEPSEEK_CONFIG_PATH` and passes `--crime-root` so all paths resolve under `general-story/`.

## Implemented (matches crime-section behaviour)

| Area | Notes |
|------|--------|
| DeepSeek Stages 1–4 | Same CLI (`--story`, `--max-step`, `--force`, `--batch`, Stage B segments, etc.). |
| `run_with_params.sh` | Same env overrides (`STORY`, `MAX_STEP`, `FORCE`, …) and argv assembly pattern. |
| `run_deepseek_pipeline.sh` | Loads repo `.env`, forwards argv to local `helper/deepseek_pipeline.py`. |
| `deepseek.config.example.ini` | Same knob layout; **separate file** so defaults are not crime-section’s. |
| `requirements-deepseek.txt` | Present. |
| `story-to-run/story.txt` | Default script source for sync into `FULL_STORY.txt`. |
| `bifuracted-template/` | Stage A/B/C + `character.txt` — **general-story copy** (content differs; placeholders must stay engine-compatible). |
| `helper/create-story-skelton` | Bash skeleton + paste steps 2–4. |
| `helper/create-story-skelton-auto` | Claude A+B+C wrapper (needs `anthropic`, `ANTHROPIC_API_KEY`). |
| `helper/auto_pipeline.py` | Same role as crime-section; use `--root "$(pwd)"` from `general-story/`. |
| `helper/README.md` | Documents helpers + `cd general-story` expectation. |
| `helper/image-mapping` | Present (same auxiliary asset pattern as crime-section). |

## Intentionally different or optional

| Area | crime-section | general-story |
|------|----------------|---------------|
| `helper/deepseek_pipeline.py` | Full implementation | Launcher → `exec` shared engine |
| `template/` prompts (`story-writing`, `story-writing-master-prompt`, `title-thumbnailtext`) | Checked in | **Not** bundled — optional; see [`template/README.md`](template/README.md). |
| `library/` (sample transcripts) | Present | **Not** bundled — copy only if you want offline references in-package. |
| Default story slug in `run_with_params.sh` | e.g. `spain-horror` | e.g. `sample-story` (edit **`MY_FOLDER_NAME`**). |

## Claude path

Install SDK when using auto mode:

```bash
pip install -r requirements-claude.txt
```

(or `pip install anthropic`).

## Placeholder contract

Stage templates must keep the markers and placeholders the engine expects (`PH_*`, `PART 3 — INPUT SLOTS`, etc.). Source of truth: constants and comments in `crime-section/helper/deepseek_pipeline.py`.
