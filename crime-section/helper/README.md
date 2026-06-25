# `create-story-skelton` (crime-section)

Bash helper that provisions a story folder under `crime-section/stories/<slug>/` and, in later steps, pastes workspace files into Stage A/B/C Markdown templates copied from `crime-section/bifuracted-template/`.

**Run everything from the `crime-section` directory** (the parent of this `helper/` folder), or invoke with `bash crime-section/helper/create-story-skelton` from the repo root.

## Requirements

- **Bash** (script uses `set -euo pipefail`)
- **Python 3** (steps 2–4 rewrite template files via a small stdin script)

## Quick start

1. Open [`create-story-skelton`](./create-story-skelton).
2. Set **`STORY_NAME`** to your story slug (e.g. `myStory2026`).
3. Set **`STAGE`** to the operation you want (see below).
4. Run from `crime-section` (or pass the full path to `bash` as shown below):

```bash
cd crime-section
bash helper/create-story-skelton
```

Or from repo root: `bash crime-section/helper/create-story-skelton`. Make executable once: `chmod +x helper/create-story-skelton`, then `./helper/create-story-skelton` from `crime-section`.

## Configuration (top of the script)

| Variable       | Purpose |
|----------------|---------|
| `STORY_NAME`   | Story slug; becomes `stories/<STORY_NAME>/`. Must be a single path segment (no `/` or `..`). |
| `STAGE`        | Which step runs (see next section). Case-insensitive; spaces are stripped. |

## Stages

Only one stage runs per invocation.

| `STAGE` values | What it does |
|----------------|--------------|
| *(empty)*, `1`, `step1`, `stage1` | **Create skeleton** — creates `stories/<STORY_NAME>/` if it does not exist; copies templates from `bifuracted-template/` into `template/` with story-specific names; creates empty root files. **Fails** if `stories/<STORY_NAME>` already exists. |
| `2`, `step2`, `stage2` | **Fill Stage A config template** — replaces the full-story placeholder in `template/STORY_Config_<STORY_NAME>.md` with the contents of `FULL_STORY.txt`. |
| `3`, `step3`, `stage3` | **Fill Stage B scene breakdown** — injects `output_config_<STORY_NAME>.md` and `FULL_STORY.txt` into `template/Story_scene_breakdown_<STORY_NAME>.md`. |
| `4`, `step4`, `stage4` | **Fill Stage C image/motion** — injects `output_config_<STORY_NAME>.md` and `output_story_breakdown_<STORY_NAME>.md` into `template/<STORY_NAME>_stage-c-image-motion.md`. |

### Step 1 layout

Under `stories/<STORY_NAME>/`:

**Root**

- `FULL_STORY.txt`
- `output_config_<STORY_NAME>.md`
- `output_story_breakdown_<STORY_NAME>.md`
- `prompt.txt`

**`template/`** (from `bifuracted-template/`, with renames)

| Source in `bifuracted-template/` | Destination |
|-----------------------------------|-------------|
| `stage-a-story-config.md` | `STORY_Config_<STORY_NAME>.md` |
| `stage-b-scene-breakdown.md` | `Story_scene_breakdown_<STORY_NAME>.md` |
| Any other regular file *(except `readme.md`, case-insensitive)* | `<STORY_NAME>_<original-basename>` |

So the Stage C template becomes `<STORY_NAME>_stage-c-image-motion.md` when the source is `stage-c-image-motion.md`.

## Command-line overrides

Behaviour matches the embedded comments in the script:

| Invocation | Effect |
|------------|--------|
| `bash helper/create-story-skelton` | Uses `STORY_NAME` and `STAGE` from the script. |
| `bash helper/create-story-skelton <slug>` | Uses `STAGE` from the script; **`STORY_NAME` = `<slug>`** for this run. |
| `bash helper/create-story-skelton step <1\|2\|3\|4> [<slug>]` | Forces that step for this run; optional slug overrides story name (`step` or `stage` keyword both work). |
| `bash helper/create-story-skelton <1\|2\|3\|4>` | Shorthand to run that step only (story name still from the script unless you combine with patterns above — see script `parse_cmdline`). |

Notes:

- Passing **exactly two** arguments that do **not** form `step|stage` + digit triggers **usage** and exit (by design).
- Single-argument aliases like `step2`, `stage3`, `2`, etc. force that step without changing `STORY_NAME`.

## Placeholders (steps 2–4)

The Python snippets replace the **first** occurrence of each placeholder. If a template was already filled or the template text changed, the script exits with an error.

| Step | Placeholder in template |
|------|-------------------------|
| 2 | `{Paste the full Hindi / Hinglish / English story here.}` |
| 3 | `{Paste the STORY CONFIG BLOCK output from Stage A here.}` and `{Paste the full Hindi / Hinglish / English story here — same as used in Stage A.}` |
| 4 | `{Paste the STORY CONFIG BLOCK output from Stage A here.}` and `{Paste the LOCKED SCENE BREAKDOWN output from Stage B here.}` |

## Paths the script assumes

- **Crime-section root:** parent of this `helper/` directory (`ROOT` = `crime-section/`).
- Stories: `ROOT/stories/`
- Templates source: `ROOT/bifuracted-template/`

## Typical workflow

1. Set `STORY_NAME`, `STAGE=""` or `1`, run once → skeleton.
2. Fill `FULL_STORY.txt` (and later `output_config_*.md`, `output_story_breakdown_*.md` as you produce them).
3. Run `STAGE=2`, then `3`, then `4` (or use CLI `step 2`, etc.) to merge those files into the templates.

## Auto mode (`create-story-skelton-auto`)

A sibling script, [`create-story-skelton-auto`](./create-story-skelton-auto), is a superset of `create-story-skelton`: it accepts every existing `STAGE` value and adds one more — `auto` — which runs Stage A + Stage B + Stage C end-to-end against Claude (Anthropic API) so you do not have to paste templates into ChatGPT yourself.

### Requirements (auto stage only)

- `ANTHROPIC_API_KEY` exported in your shell.
- `pip install anthropic` (uses the Anthropic Python SDK).
- An already-created skeleton (`step1`) with `FULL_STORY.txt` populated.

### Env knobs (top of script, env-overridable)

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODEL` | `claude-opus-4-7` | Anthropic model id used for all 3 stages. As of May 2026 the latest Opus is `claude-opus-4-7` (Opus 4.7). Set to `claude-sonnet-4-6` if you want the cheaper/faster Sonnet 4.6. |
| `STAGE_C_BATCH` | `8` | Scenes per Stage C call. Smaller is safer; larger may hit `max_tokens`. |
| `INCLUDE_CHARACTER_LIBRARY` | `1` | If `1`, inject `template/character.txt` into every `CHARACTER_LIBRARY:` slot. Set to `0` to send `NONE` instead. |
| `FORCE` | `0` | If `1`, re-run stages even if their outputs are already non-empty. |
| `GENRE` | *(empty)* | Optional genre/tone hint passed into Stage A's `OPTIONAL_GENRE_OR_TONE:` slot. |

### Typical flow

```bash
cd crime-section
export ANTHROPIC_API_KEY=sk-ant-...
bash helper/create-story-skelton-auto step 1 my-story          # create skeleton
echo "<full Hindi/Hinglish/English story>" \
  > stories/my-story/FULL_STORY.txt                            # fill input
bash helper/create-story-skelton-auto auto my-story            # run A+B+C
```

Output lands in the usual places:

- `stories/my-story/output_config_my-story.md` — Stage A
- `stories/my-story/output_story_breakdown_my-story.md` — Stage B
- `stories/my-story/prompt.txt` — Stage C (image + motion prompts, all batches concatenated)

### Cost optimization (prompt caching)

Each LLM call uses `cache_control: ephemeral` system blocks so that the large static spec (PART 1 + PART 2 of each stage template, ~57–75 KB) is cached after the first request. Stage C also caches the `STORY_CONFIG_BLOCK + LOCKED_SCENE_BREAKDOWN + CHARACTER_LIBRARY` context as a second cache breakpoint, so only the `SCENE_RANGE: Scenes X-Y` line varies per Stage C call. Token usage and cache hit/miss counts are logged for every call:

```
[auto] [stage-c 3/12 (Scenes 17-24)] input=412 cache_read=42118 cache_create=0 output=8901 stop=end_turn 18.4s
```

### Resume / re-run

- If `output_config_*.md` is already non-empty, Stage A is skipped.
- Same for `output_story_breakdown_*.md` and Stage B.
- Stage C refuses to start if `prompt.txt` is non-empty (to avoid double-appending).
- Pass `FORCE=1` to override these guards.
