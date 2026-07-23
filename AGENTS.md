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
URL,duration_minutes,story_type[,folder_name]
```

Example:
```
https://www.youtube.com/watch?v=TUvVM05QXOE,12,crime
```

**Story types:** `crime` | `general` | `english` | `god`

**Pipeline:**
1. Download seed + related YouTube transcripts → `research-storage-stories/` (default: 5 related videos via `--related`)
2. Combine transcripts → build type-specific prompt with duration (1 min = 1,000 chars for Hindi prompts)
3. Generate via **claude.ai in Chrome** (default) — paste prompt into https://claude.ai/new
4. Save to `research-storage-stories/{topic}-research/outputfinal/`

**Common flags:**
```bash
./story-agent/run.sh --research-only          # transcripts only
./story-agent/run.sh --prepare-only           # prompt only
./story-agent/run.sh --video-url URL --type crime --duration 5 --related 5
```

**Setup:** `pip install -r story-agent/requirements.txt` and `playwright install chromium`

**Generate (default):** claude.ai in your browser — not Cursor CLI.

```bash
# Terminal 1 — keep open
./story-agent/start-debug-browser.sh

# Terminal 2
./story-agent/run.sh
```

Use `--mode claude-code` for Cursor CLI, or `--mode api` with `ANTHROPIC_API_KEY`.

**Code layout:**
- `story-agent/story_agent.py` — CLI + orchestration
- `library/story_research.py` — transcript download
- `library/story_generate.py` — prompts + LLM calls

