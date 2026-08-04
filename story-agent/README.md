# Story Agent

One pipeline for YouTube story production: **research transcripts → build prompt → generate script**.

Supports four story types: **crime**, **general**, **english**, and **god**.

## What it does

For each job in your queue:

1. **Download** — your provided YouTube URLs only (3–6 typical; **no auto search**)
2. **Pointers** *(default for crime/general/god)* — DeepSeek extracts 20–25 story pointers per transcript → `story_pointers.txt`
3. **Prompt** — injects pointers into `master-story-prompt-v3-nitish-flow-universal` (or raw transcripts into legacy prompts)
4. **Generate** — sends the prompt to Claude (default: claude.ai in Chrome)
5. **Save** — writes `FULL_STORY.txt` (extracted from FULL SCRIPT section), pointers, prompt, and metadata to `outputfinal/`

```
YouTube URL  →  research-storage-stories/{case}-research/  →  DeepSeek pointers  →  Claude  →  .../outputfinal/
```

Legacy mode (`--raw-transcripts`): skips pointer extraction and uses combined raw transcripts with the older per-type master prompts.

## Setup

From the repo root:

```bash
pip install -r story-agent/requirements.txt
playwright install chromium
```

**Browser mode (default):** uses your logged-in session at [claude.ai/new](https://claude.ai/new) — not Cursor.

```bash
# Terminal 1 — quit Chrome first, then:
./story-agent/start-debug-browser.sh

# Terminal 2
./story-agent/run.sh
```

Pick **Sonnet** in the claude.ai UI if prompted. The agent pastes the prompt and waits for the full response.

Optional: add `DEEPSEEK_API_KEY` to `.env` for bullet pointer extraction (default pipeline).
Optional: add `ANTHROPIC_API_KEY` to `.env` for `--mode api`.

## Quick start

Edit `story-agent/queue.txt`, then run:

```bash
./story-agent/run.sh
```

Check progress:

```bash
python3 story-agent/story_agent.py --status
```

## Queue format

One story per line in `story-agent/queue.txt`:

```
URL1|URL2|URL3|...,duration_minutes,story_type[,folder_name]
```

| Field | Example | Description |
|-------|---------|-------------|
| URLs | `https://...v=A\|https://...v=B\|https://...v=C` | **You provide all sources** (pipe-separated). First = seed. No auto search. |
| duration_minutes | `30` | Target story length (1 min = 1,000 Hindi chars) |
| story_type | `general` | `crime` \| `general` \| `english` \| `god` |
| folder_name | `126-khamenei-research` | Optional research folder under `research-storage-stories/` |

Lines starting with `#` and blank lines are ignored.

**Node 126 example (queue line):**
```
https://www.youtube.com/watch?v=tsAimcI66bo|https://www.youtube.com/watch?v=RiFAwUGHjxw|https://www.youtube.com/watch?v=_SH-lINJoZQ|https://www.youtube.com/watch?v=W-mcJrfn4hQ,30,general,126-khamenei-research
```

**Or use a URLs file** (easier for 4–6 links):

```bash
./story-agent/run.sh \
  --urls-file story-agent/jobs/126-khamenei.urls.txt \
  --type general \
  --duration 30 \
  --folder 126-khamenei-research
```

## Story types

| Type | Default pipeline | Master prompt | Output language |
|------|------------------|---------------|-----------------|
| `crime` | bullet pointers + v3 | `story-making-prompts/master-story-prompt-v3-nitish-flow-universal` | Hindi |
| `general` | bullet pointers + v3 | `story-making-prompts/master-story-prompt-v3-nitish-flow-universal` | Hindi |
| `english` | raw transcripts | `story-making-prompts/english-story-master` | English |
| `god` | bullet pointers + v3 | `story-making-prompts/master-story-prompt-v3-nitish-flow-universal` | Hindi |

Target story length = `duration_minutes × 1,000` Hindi characters (override with `--target-chars` or `--extra-chars`).

Pointer extraction uses `bullet-pointers.txt` and DeepSeek (`documentary-engine/deepseek.config.ini`).

## Common commands

```bash
# Full pipeline from queue.txt
./story-agent/run.sh

# Download transcripts only (no pointers, no Claude)
./story-agent/run.sh --research-only

# Extract DeepSeek bullet pointers only (after research)
./story-agent/run.sh --pointers-only

# Build prompt only — verify before spending Claude time
./story-agent/run.sh --prepare-only

# Legacy: raw combined transcripts + old master prompts
./story-agent/run.sh --raw-transcripts

# Generate from existing research folder
./story-agent/run.sh --generate-only \
  --research-dir research-storage-stories/ketan-agarwal-case-research \
  --video-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --type crime

# Re-run a job that was already processed
./story-agent/run.sh --force

# Browser mode (default — claude.ai in Chrome)
./story-agent/start-debug-browser.sh   # terminal 1
./story-agent/run.sh                   # terminal 2

# Cursor / Claude Code CLI instead of browser
./story-agent/run.sh --mode claude-code

# Anthropic API
./story-agent/run.sh --mode api
```

## Output locations

### Research (transcripts)

```
research-storage-stories/{topic}-research/
├── {Video Title}.txt       # plain transcript per video
├── videos.json             # metadata, sorted by views
├── research-meta.json      # seed URL, search query, counts
├── bullet_extract_raw/     # per-video DeepSeek pointer output
├── story_pointers.txt      # merged pointer ledger (default pipeline input)
├── story_pointers-meta.json
└── outputfinal/            # generated story
    ├── FULL_STORY.txt      # final Hindi script (FULL SCRIPT section only)
    ├── story_pointers.txt  # copy of merged ledger
    ├── prompt.txt
    ├── raw.md              # full Claude response (not the deliverable)
    └── meta.json
```

**Example:**

```
research-storage-stories/ketan-agarwal-case-research/outputfinal/FULL_STORY.txt
```

Processed jobs are tracked in `story-agent/output/processed.json`. Already-done jobs are skipped unless you pass `--force`.

## Git — what not to commit

Story **data** stays local (see `.gitignore`):

| Ignored | Contents |
|---------|----------|
| `research-storage-stories/**/outputfinal/` | Generated scripts, prompts, raw Claude output |
| `story-agent/output/processed.json` | Job dedup state only |
| `*/story-to-run/*` (except `queue.txt`) | Raw story scripts |
| `*/stories/` | Pipeline-generated scene/prompt outputs |

Only **code, prompts, and queue config** belong in git.

## Project layout

```
story-agent/
├── run.sh              # entry point
├── story_agent.py      # CLI + orchestration
├── queue.txt           # your batch queue
├── requirements.txt
└── output/             # generated stories

library/
├── fetch_youtube_transcript.py   # YouTube metadata + captions
├── story_research.py             # seed + related video download
├── bullet_pointers.py            # DeepSeek per-transcript pointer extraction
├── deepseek_client.py            # DeepSeek API client
└── story_generate.py             # prompts + Claude/API/browser calls
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named 'library'` | Run from repo root via `./story-agent/run.sh` (sets `PYTHONPATH`). Ensure `library/` exists and is committed. |
| `DEEPSEEK_API_KEY not set` | Add to repo-root `.env` for default bullet-pointer pipeline |
| `Claude Code CLI not found` | Install from [claude.ai/code](https://claude.ai/code), then `claude auth login` |
| No transcript for a video | Try `--lang hi en`; video may lack captions |
| Already processed | Use `--force` or pick another video |
| Long story times out | Increase `--timeout 3600` (default is 1 hour) |
| `pipe-separated YouTube URLs required` | Provide 2+ URLs via `--urls-file`, `--video-urls`, or `URL1\|URL2\|URL3` in queue |

## Next steps after generation

The `FULL_STORY.txt` output can feed into the downstream storyboard pipelines:

- **Crime:** `crime-section/run_with_params.sh`
- **General:** `general-story/run_with_params.sh`
- **English:** `english-story/run_with_params.sh`

Copy or symlink the script into the appropriate `story-to-run/` folder and continue with Stages A → B → C (scene breakdown + image prompts).
