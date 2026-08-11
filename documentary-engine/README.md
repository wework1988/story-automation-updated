# Research Engine — Channel-First YouTube Research

Simple tool: give a YouTube URL → search **your priority channels first** → download 3–4 transcripts → combine into one research file for your master story prompt.

No LLM agents. No DeepSeek. No script generation here.

## Setup

```bash
cd documentary-engine
./run.sh --help   # auto-creates .venv on first run
```

## Quick start

```bash
# Single URL
./run.sh --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom output folder
./run.sh --url "https://www.youtube.com/watch?v=VIDEO_ID" --folder kandhar-hijack

# Queue file (one URL per line)
./run.sh
```

## Priority channels (searched first)

1. [@NitishRajput](https://www.youtube.com/@NitishRajput)
2. [@TheLallantop](https://www.youtube.com/@TheLallantop)
3. [@Khabargaon](https://www.youtube.com/@Khabargaon)
4. [@mightymonkofficial](https://www.youtube.com/@mightymonkofficial)
5. [@dhruvrathee](https://www.youtube.com/@dhruvrathee)

## How it works

1. Extract topic from seed video title
2. Search each priority channel for that topic
3. If **3+ relevant videos** found on those channels → use **only** those (up to 4)
4. If fewer than 3 → fill remaining slots from general YouTube search
5. Download transcripts
6. Order: seed video first, then by upload date (timeline flow)
7. Write `COMBINED_RESEARCH.txt` — paste this into your master prompt

## Output

```
storage/{folder}/
  transcripts/           # individual .txt files
  videos.json            # metadata for each source
  research-meta.json     # search query, channel stats
  COMBINED_RESEARCH.txt  # ordered combined research → use with your master prompt
```

## Then generate your story

Use `COMBINED_RESEARCH.txt` as input to your existing story pipeline:

```bash
# story-agent (separate step)
./story-agent/run.sh --prepare-only --video-url URL --type general --duration 10
# paste COMBINED_RESEARCH.txt content where transcript goes, or point research-dir
```

## Copyright note

This workflow helps reduce risk but is **not a legal guarantee**:

- **Facts and events** (dates, names, what happened) are not copyrightable
- **Expression** (exact wording, narration style, unique phrasing) is copyrightable
- Using transcripts as **research** and rewriting with your master prompt = transformative original work
- **Do not** copy sentences or narration structure from source videos
- Your master prompt should instruct: facts only, original Hindi narration, no phrase copying

The old multi-agent documentary pipeline (`documentary_engine.py`, DeepSeek agents) is deprecated — use this research engine + your story-agent master prompt instead.
