# Story Agent

One pipeline for YouTube story production: **research transcripts → build prompt → generate script**.

Supports four story types: **crime**, **general**, **english**, and **god**.

## What it does

For each job in your queue:

1. **Research** — downloads the seed video transcript plus related high-view videos on the same topic
2. **Combine** — merges all transcripts into one source block
3. **Prompt** — injects the source into the correct master prompt for the story type
4. **Generate** — sends the prompt to Claude (default: Claude Code CLI)
5. **Save** — writes the final story and metadata to `story-agent/output/`

```
YouTube URL  →  research-storage-stories/  →  Claude  →  story-agent/output/{type}/{slug}/
```

## Setup

From the repo root:

```bash
pip install -r story-agent/requirements.txt
claude auth login          # one-time; uses your claude.ai Pro login
claude auth status         # should show loggedIn: true
```

Optional: add `ANTHROPIC_API_KEY` to the repo `.env` if you want `--mode api` instead of Claude Code CLI.

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
URL,related_count,story_type[,folder_name]
```

| Field | Example | Description |
|-------|---------|-------------|
| URL | `https://www.youtube.com/watch?v=VIDEO_ID` | Seed YouTube video |
| related_count | `25` | How many related videos to download (0 = seed only) |
| story_type | `crime` | `crime` \| `general` \| `english` \| `god` |
| folder_name | `my-case-research` | Optional research folder name under `research-storage-stories/` |

Lines starting with `#` and blank lines are ignored.

**Examples:**

```
https://www.youtube.com/watch?v=_rZLnotPd5Y,22,crime
https://www.youtube.com/watch?v=ABC123,5,general
https://www.youtube.com/watch?v=XYZ789,10,english
https://www.youtube.com/watch?v=GOD123,3,god,my-ekadashi-research
```

### Single video (no queue file)

```bash
./story-agent/run.sh \
  --video-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --type crime \
  --related 25
```

## Story types

| Type | Master prompt | Output language |
|------|---------------|-----------------|
| `crime` | `story-making-prompts/crime-story-claude-19th-june-with-characters` | Hindi |
| `general` | `story-making-prompts/v1-claude-latest-19june-with-charaacters` | Hindi |
| `english` | `story-making-prompts/english-story-master` | English |
| `god` | Same as general + mythology/devotional notes | Hindi |

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

# Use Anthropic API instead of Claude Code CLI
./story-agent/run.sh --mode api

# Browser mode (logged-in Chrome on claude.ai)
./story-agent/start-debug-browser.sh   # in a separate terminal, if needed
./story-agent/run.sh --mode browser
```

## Output locations

### Research (transcripts)

```
research-storage-stories/{topic}-research/
├── {Video Title}.txt       # plain transcript per video
├── videos.json             # metadata, sorted by views
└── research-meta.json      # seed URL, search query, counts
```

### Generated stories

```
story-agent/output/{type}/{slug}/
├── FULL_STORY.txt          # final script (extract FULL SCRIPT section)
├── prompt.txt              # prompt sent to Claude
├── raw.md                  # full Claude response
└── meta.json               # char counts, video URL, timestamps
```

Processed jobs are tracked in `story-agent/output/processed.json`. Already-done jobs are skipped unless you pass `--force`.

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
