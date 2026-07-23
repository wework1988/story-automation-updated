# Story Agent

One pipeline for YouTube story production: **research transcripts → build prompt → generate script**.

Supports four story types: **crime**, **general**, **english**, and **god**.

## What it does

For each job in your queue:

1. **Research** — downloads the seed video transcript plus related high-view videos on the same topic
2. **Combine** — merges all transcripts into one source block
3. **Prompt** — injects the source into the correct master prompt for the story type
4. **Generate** — sends the prompt to Claude (default: Claude Code CLI)
5. **Save** — writes the final story and metadata to `research-storage-stories/{case}-research/outputfinal/`

```
YouTube URL  →  research-storage-stories/{case}-research/  →  Claude  →  .../outputfinal/
```

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

Optional: `claude auth login` only if you use `--mode claude-code` (Cursor CLI).
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
URL,duration_minutes,story_type[,folder_name]
```

| Field | Example | Description |
|-------|---------|-------------|
| URL | `https://www.youtube.com/watch?v=VIDEO_ID` | Seed YouTube video |
| duration_minutes | `5` | Target story length in minutes (crime/general: 1 min = 1,000 Hindi chars) |
| story_type | `crime` | `crime` \| `general` \| `english` \| `god` |
| folder_name | `my-case-research` | Optional research folder name under `research-storage-stories/` |

Related videos for research default to **5** (override with `--related 3` on the command line).

Lines starting with `#` and blank lines are ignored.

**Examples:**

```
https://www.youtube.com/watch?v=_rZLnotPd5Y,5,crime
https://www.youtube.com/watch?v=ABC123,12,general
https://www.youtube.com/watch?v=XYZ789,15,english
https://www.youtube.com/watch?v=GOD123,10,god,my-ekadashi-research
```

### Single video (no queue file)

```bash
./story-agent/run.sh \
  --video-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --type crime \
  --duration 5 \
  --related 5
```

## Story types

| Type | Master prompt | Output language |
|------|---------------|-----------------|
| `crime` | `story-making-prompts/crime-story-claude-19th-june-with-characters` | Hindi |
| `general` | `story-making-prompts/v1-claude-latest-19june-with-charaacters` | Hindi |
| `english` | `story-making-prompts/english-story-master` | English |
| `god` | `story-making-prompts/god story` | Hindi |

Target story length = combined transcript length **+ 1,000 characters** (override with `--extra-chars`).

## Common commands

```bash
# Full pipeline from queue.txt
./story-agent/run.sh

# Download transcripts only (no Claude call)
./story-agent/run.sh --research-only

# Build prompt only — verify before spending Claude time
./story-agent/run.sh --prepare-only

# Generate from existing research folder
./story-agent/run.sh --generate-only \
  --research-dir research-storage-stories/ketan-agarwal-case-research \
  --video-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --type crime

# Re-run a job that was already processed
./story-agent/run.sh --force

# Lower view threshold for related videos
./story-agent/run.sh --min-views 5000

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
└── research-meta.json      # seed URL, search query, counts
```

### Generated stories (same research folder)

```
research-storage-stories/{topic}-research/
├── {Video Title}.txt       # transcripts (step 1)
├── videos.json
├── research-meta.json
└── outputfinal/            # generated story (step 2)
    ├── FULL_STORY.txt      # final script — main file
    ├── prompt.txt
    ├── raw.md
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
└── story_generate.py             # prompts + Claude/API/browser calls
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named 'library'` | Run from repo root via `./story-agent/run.sh` (sets `PYTHONPATH`). Ensure `library/` exists and is committed. |
| `Claude Code CLI not found` | Install from [claude.ai/code](https://claude.ai/code), then `claude auth login` |
| No transcript for a video | Try `--lang hi en`; video may lack captions |
| Already processed | Use `--force` or pick another video |
| Long story times out | Increase `--timeout 3600` (default is 1 hour) |
| Related videos not found | Lower `--min-views 5000` or increase `--related` |

## Next steps after generation

The `FULL_STORY.txt` output can feed into the downstream storyboard pipelines:

- **Crime:** `crime-section/run_with_params.sh`
- **General:** `general-story/run_with_params.sh`
- **English:** `english-story/run_with_params.sh`

Copy or symlink the script into the appropriate `story-to-run/` folder and continue with Stages A → B → C (scene breakdown + image prompts).
