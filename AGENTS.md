# AI Agents — Research Story Automation

## Story Agent (unified)

**Purpose:** One agent for everything — research YouTube transcripts + generate stories by type.

**Skill:** `.cursor/skills/story-agent/SKILL.md`

**Entry point:**
```bash
./story-agent/run.sh
```

**Queue format** (`story-agent/queue.txt`):
```
URL,related_count,story_type[,folder_name]
```

Example:
```
https://www.youtube.com/watch?v=TUvVM05QXOE,25,crime
```

**Story types:** `crime` | `general` | `english` | `god`

**Pipeline:**
1. Download seed + related YouTube transcripts → `research-storage-stories/`
2. Combine transcripts → build type-specific prompt
3. Generate via Claude Code CLI (default)
4. Save to `story-agent/output/{type}/{slug}/`

**Common flags:**
```bash
./story-agent/run.sh --research-only          # transcripts only
./story-agent/run.sh --prepare-only           # prompt only
./story-agent/run.sh --video-url URL --type crime --related 25
```

**Setup:** `pip install -r story-agent/requirements.txt` and `claude auth login`

**Code layout:**
- `story-agent/story_agent.py` — CLI + orchestration
- `library/story_research.py` — transcript download
- `library/story_generate.py` — prompts + LLM calls

