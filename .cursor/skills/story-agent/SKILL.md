---
name: story-agent
description: >-
  Unified story agent: you provide 3–6 YouTube URLs → download transcripts
  → DeepSeek bullet pointers → Nitish v3 master prompt → generate story
  (crime/general/english/god) via claude.ai browser. No auto YouTube search.
---

# Story Agent

**You provide all YouTube URLs.** No automatic related-video search.

## Queue format

Edit `story-agent/queue.txt`:
```
URL1|URL2|URL3|...,duration_minutes,story_type[,folder_name]
```

First URL = seed (title/metadata). Rest = research sources (3–6 typical).

Types: `crime` | `general` | `english` | `god`

## Commands

```bash
# URLs file (recommended for 4–6 links)
./story-agent/run.sh \
  --urls-file story-agent/jobs/126-khamenei.urls.txt \
  --type general --duration 30 --folder 126-khamenei-research

# Inline URLs
./story-agent/run.sh --video-urls URL1 URL2 URL3 URL4 --type general --duration 30

./story-agent/run.sh --research-only    # download transcripts only
./story-agent/run.sh --pointers-only    # + DeepSeek pointers
./story-agent/run.sh --prepare-only     # prompt only
python3 story-agent/story_agent.py --status
```

## Output

| Path | Contents |
|------|----------|
| `research-storage-stories/{folder}/` | Transcripts, `story_pointers.txt` |
| `.../outputfinal/` | FULL_STORY.txt, prompt, meta |

## Setup

```bash
pip install -r story-agent/requirements.txt
playwright install chromium
# .env: DEEPSEEK_API_KEY
# Browser: ./story-agent/start-debug-browser.sh then ./story-agent/run.sh
```
