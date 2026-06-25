---
name: story-agent
description: >-
  Unified story agent: queue file or single URL → research YouTube transcripts
  → generate story by type (crime/general/english/god) via Claude Code CLI.
  Use for story-agent, queue.txt, batch stories, research + generate, or any
  YouTube-to-story workflow.
---

# Story Agent

Single agent: **queue → research → generate → `story-agent/output/`**

## Queue format

Edit `story-agent/queue.txt`:
```
URL,related_count,story_type[,folder_name]
```

Types: `crime` | `general` | `english` | `god`

## Commands

```bash
./story-agent/run.sh                                    # full pipeline from queue
./story-agent/run.sh --video-url URL --type crime --related 25
./story-agent/run.sh --research-only                    # transcripts only
./story-agent/run.sh --prepare-only                     # prompt only, no LLM
./story-agent/run.sh --generate-only --research-dir research-storage-stories/FOLDER
python3 story-agent/story_agent.py --status
```

## Output

| Path | Contents |
|------|----------|
| `research-storage-stories/{topic}-research/` | Transcripts + videos.json |
| `story-agent/output/{type}/{slug}/FULL_STORY.txt` | Final story |
| same folder | `raw.md`, `prompt.txt`, `meta.json` |

## Prompts by type

| Type | File |
|------|------|
| crime | `story-making-prompts/crime-story-claude-19th-june-with-characters` |
| general | `story-making-prompts/v1-claude-latest-19june-with-charaacters` |
| english | `story-making-prompts/english-story-master` |
| god | general prompt + mythology notes |

## Setup

```bash
pip install -r story-agent/requirements.txt
claude auth login
```
