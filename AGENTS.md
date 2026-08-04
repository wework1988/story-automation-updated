# AI Agents — Research Story Automation

## Story Agent (unified)

**Purpose:** Download your YouTube URLs → bullet pointers → generate stories by type. **No auto YouTube search.**

**Skill:** `.cursor/skills/story-agent/SKILL.md`

**Entry point:**
```bash
./story-agent/run.sh
```

**Queue format** (`story-agent/queue.txt`):
```
URL1|URL2|URL3|...,duration_minutes,story_type[,folder_name]
```

Example (4 sources, 30 min):
```
https://www.youtube.com/watch?v=tsAimcI66bo|https://www.youtube.com/watch?v=RiFAwUGHjxw|https://www.youtube.com/watch?v=_SH-lINJoZQ|https://www.youtube.com/watch?v=W-mcJrfn4hQ,30,general,126-khamenei-research
```

**Story types:** `crime` | `general` | `english` | `god`

**Pipeline:**
1. Download **your** YouTube URLs (pipe-separated queue, `--urls-file`, or `--video-urls`) — **no auto search**
2. DeepSeek bullet pointers per transcript → `story_pointers.txt`
3. Build Nitish v3 master prompt with pointer ledger
4. Generate via **claude.ai in Chrome** (default)
5. Save clean `FULL_STORY.txt` to `outputfinal/`

**Common flags:**
```bash
./story-agent/run.sh --urls-file story-agent/jobs/126-khamenei.urls.txt --type general --duration 30
./story-agent/run.sh --research-only   # transcripts only
./story-agent/run.sh --pointers-only   # transcripts + DeepSeek pointers
./story-agent/run.sh --prepare-only    # prompt only
```

**Setup:** `pip install -r story-agent/requirements.txt`, `playwright install chromium`, `DEEPSEEK_API_KEY` in `.env`

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
- `library/bullet_pointers.py` — DeepSeek pointer extraction + ledger merge
- `library/deepseek_client.py` — DeepSeek API client
- `library/story_generate.py` — prompts + LLM calls

