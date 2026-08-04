#!/usr/bin/env python3
"""Story generation: build prompts by type, call Claude, save output."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

from library.fetch_youtube_transcript import slug_title  # noqa: E402

DEFAULT_CHROME_USER_DATA = Path.home() / "Library/Application Support/Google/Chrome"
DEFAULT_FIREFOX_PROFILE = "Default"  # Chrome profile-directory name (CLI compat)
STATE_FILE = "processed.json"

INPUT_SOURCE = "[paste here]"
INPUT_LENGTH = "[e.g. 12,000 characters or 18 min]"

STORY_TYPES = ("crime", "general", "english", "god")

PROMPTS = {
    "crime": REPO_ROOT / "story-making-prompts/crime-story-claude-19th-june-with-characters",
    "general": REPO_ROOT / "story-making-prompts/v1-claude-latest-19june-with-charaacters",
    "english": REPO_ROOT / "story-making-prompts/english-story-master",
    "god": REPO_ROOT / "story-making-prompts/god story",
}

# Nitish-flow v3 master prompt — used with bullet-pointer research ledger
V3_MASTER_PROMPT = REPO_ROOT / "story-making-prompts/master-story-prompt-v3-nitish-flow-universal"
V3_SOURCE_PLACEHOLDER = "[paste COMBINED_RESEARCH.txt content here]"
V3_LENGTH_PLACEHOLDER = "[e.g. 12,000 characters or 12 min]"
LENGTH_TOLERANCE = 500


def load_prompt_template(prompt_path: Path, story_type: str) -> str:
    if not prompt_path.is_file():
        raise FileNotFoundError(
            f"No prompt file for story type {story_type!r}: {prompt_path}"
        )
    template = prompt_path.read_text(encoding="utf-8").strip()
    if not template:
        raise ValueError(
            f"Prompt file for {story_type!r} is empty: {prompt_path}. "
            "Add your master prompt text before running."
        )
    return template


def log(msg: str) -> None:
    print(f"[generate] {msg}", flush=True)


def load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_state(output_dir: Path) -> dict:
    path = output_dir / STATE_FILE
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"processed": {}}


def save_state(output_dir: Path, state: dict) -> None:
    path = output_dir / STATE_FILE
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def story_slug(title: str) -> str:
    base = slug_title(title)
    slug = re.sub(r"[^\w\s-]", "", base, flags=re.UNICODE)
    slug = re.sub(r"[\s_]+", "-", slug.strip()).strip("-").lower()
    return slug or "untitled-story"


def build_prompt(master_prompt_path: Path, transcript: str, target_chars: int) -> str:
    return build_prompt_for_type("general", master_prompt_path, transcript, target_chars)


def build_prompt_for_type(
    story_type: str,
    prompt_path: Path,
    source: str,
    target_chars: int,
    *,
    duration_minutes: int | None = None,
) -> str:
    template = load_prompt_template(prompt_path, story_type)
    if duration_minutes is not None:
        length_line = format_length_line(story_type, duration_minutes, target_chars)
    else:
        length_line = f"{target_chars:,} characters"

    if story_type == "english":
        prompt = template.replace("[PASTE RAW STORY HERE]", source, 1)
        prompt = prompt.replace(
            "[Example: 8 min / 12 min / 15 min / 20 min / 25 min / Shorts 30 sec / Shorts 60 sec]",
            length_line,
            1,
        )
        words_approx = max(target_chars // 6, 800)
        if duration_minutes is not None:
            words_low = duration_minutes * 130
            words_high = duration_minutes * 150
            word_range = f"{words_low:,}–{words_high:,} words"
        else:
            word_range = f"approximately {words_approx:,} words"
        prompt = prompt.replace("[INSERT TARGET LENGTH]", length_line, 1)
        prompt = prompt.replace(
            "[INSERT RANGE FROM TIME → WORD COUNT MAPPING]",
            word_range,
            1,
        )
        return prompt

    prompt = template.replace(
        f"SOURCE / RAW SCRIPT:\n{INPUT_SOURCE}",
        f"SOURCE / RAW SCRIPT:\n{source}",
        1,
    )
    prompt = prompt.replace(
        f"REQUESTED LENGTH:\n{INPUT_LENGTH}",
        f"REQUESTED LENGTH:\n{length_line}",
        1,
    )

    return prompt


def build_v3_prompt_from_pointers(
    prompt_path: Path,
    pointers_text: str,
    target_chars: int,
    *,
    duration_minutes: int | None = None,
    topic: str = "",
    story_type: str = "",
    extra_notes: str = "",
) -> str:
    """Build master-story-prompt-v3 with combined pointer ledger as SOURCE."""
    template = load_prompt_template(prompt_path, story_type or "general")
    if duration_minutes is not None:
        length_line = format_length_line("general", duration_minutes, target_chars)
    else:
        low = target_chars - LENGTH_TOLERANCE
        high = target_chars + LENGTH_TOLERANCE
        length_line = f"{target_chars:,} characters (acceptable range: {low:,} – {high:,})"

    if V3_SOURCE_PLACEHOLDER not in template:
        raise ValueError(
            f"V3 master prompt missing placeholder {V3_SOURCE_PLACEHOLDER!r}: {prompt_path}"
        )

    prompt = template.replace(V3_SOURCE_PLACEHOLDER, pointers_text.strip(), 1)
    prompt = prompt.replace(V3_LENGTH_PLACEHOLDER, length_line, 1)

    topic_line = topic.strip() if topic else "(auto-detect from pointer ledger)"
    prompt = prompt.replace(
        "TOPIC / CASE NAME:\n[optional]",
        f"TOPIC / CASE NAME:\n{topic_line}",
        1,
    )
    type_line = story_type.strip() if story_type else "auto-detect"
    prompt = prompt.replace(
        "STORY TYPE:\n[optional — else auto-detect]",
        f"STORY TYPE:\n{type_line}",
        1,
    )
    notes_block = extra_notes.strip() or (
        "Research input is pre-extracted story pointers (not raw transcripts). "
        "Merge pointers across sources; write 100% original Hindi narration."
    )
    prompt = prompt.replace(
        "ADDITIONAL NOTES:\n[optional — must-include events / sensitivity flags / Part 2 setup / tone]",
        f"ADDITIONAL NOTES:\n{notes_block}",
        1,
    )

    return prompt


def default_prompt_for_pipeline(*, use_bullet_pointers: bool, story_type: str) -> Path:
    if use_bullet_pointers and story_type in ("general", "crime", "god"):
        return V3_MASTER_PROMPT
    return PROMPTS[story_type]


def normalize_story_type(raw: str) -> str:
    value = raw.strip().lower()
    if "/" in value:
        value = value.split("/")[0].strip()
    aliases = {
        "god_story": "god",
        "gods": "god",
        "eng": "english",
        "hindi": "general",
        "military": "general",
    }
    value = aliases.get(value, value)
    if value not in STORY_TYPES:
        raise ValueError(f"Unknown story type {raw!r}. Use one of: {', '.join(STORY_TYPES)}")
    return value


STORY_TARGET_CHARS = {
    "crime": 14_000,
    "general": 14_000,
    "english": 12_000,
    "god": 14_000,
}

CHARS_PER_MINUTE = 1000


def target_chars_from_minutes(minutes: int) -> int:
    """Crime/general prompts: 1 minute = 1,000 Hindi characters."""
    return minutes * CHARS_PER_MINUTE


def format_length_line(story_type: str, duration_minutes: int, target_chars: int) -> str:
    if story_type == "english":
        words_low = duration_minutes * 130
        words_high = duration_minutes * 150
        return (
            f"{duration_minutes} min → approximately {words_low:,}–{words_high:,} words "
            f"(~{target_chars:,} characters at narration pace)"
        )
    low = target_chars - LENGTH_TOLERANCE
    high = target_chars + LENGTH_TOLERANCE
    return (
        f"{duration_minutes} min → {target_chars:,} characters "
        f"(acceptable range: {low:,} – {high:,})"
    )


def compute_target_chars(
    story_type: str,
    source_chars: int,
    video_count: int,
    *,
    duration_minutes: int | None = None,
    extra_chars: int = 0,
    target_override: int | None = None,
) -> int:
    """Output length for the script — NOT the combined research source size."""
    if target_override is not None:
        return target_override
    if duration_minutes is not None:
        return target_chars_from_minutes(duration_minutes) + extra_chars
    if video_count <= 1:
        return source_chars + extra_chars
    return STORY_TARGET_CHARS.get(story_type, 14_000) + extra_chars


def extract_full_script(text: str) -> str:
    """Prefer FULL SCRIPT section; fall back to full Claude output."""
    match = re.search(
        r"FULL SCRIPT\s*\n=+\s*\n(.*?)(?:\n=+\s*\nPOST-WRITE CHARACTER COUNT|\Z)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if match:
        body = match.group(1).strip()
        if body:
            return body
    if re.search(r"PRE-WRITE VALIDATOR", text, flags=re.I) and not re.search(
        r"FULL SCRIPT", text, flags=re.I
    ):
        raise RuntimeError(
            "Claude returned PRE-WRITE VALIDATOR only — no FULL SCRIPT section. "
            "This usually means the target length in the prompt was invalid (too large). "
            "Re-run after fixing target length, or check raw.md."
        )
    return text.strip()


def call_claude_code(prompt: str, *, model: str | None, timeout_seconds: int) -> str:
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise RuntimeError(
            "Claude Code CLI not found. Install from https://claude.ai/code and run `claude auth login`."
        )

    cmd = [claude_bin, "-p", "--tools", ""]
    if model:
        cmd.extend(["--model", model])

    log(f"Calling Claude Code CLI ({claude_bin})...")
    log(f"Prompt size: {len(prompt):,} characters — long stories may take 15–40 minutes")

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=str(REPO_ROOT),
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"Claude Code timed out after {timeout_seconds}s") from exc

    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Claude Code failed (exit {result.returncode}): {err[:800]}")

    out = result.stdout.strip()
    if not out:
        raise RuntimeError("Claude Code returned empty output")
    return out


def call_claude_api(prompt: str, *, model: str, max_tokens: int) -> str:
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set. Add it to repo .env or use --mode browser.")

    client = anthropic.Anthropic(api_key=api_key)
    log(f"Calling Claude API ({model}, max_tokens={max_tokens})...")
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    text = "".join(parts)
    if resp.stop_reason == "max_tokens":
        log("WARNING: API response hit max_tokens — output may be truncated.")
    return text


def call_claude_browser(
    prompt: str,
    *,
    cdp_url: str | None,
    chrome_user_data: Path,
    profile_directory: str,
    timeout_seconds: int,
) -> str:
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        if cdp_url:
            log(f"Connecting to Chrome over CDP: {cdp_url}")
            try:
                browser = p.chromium.connect_over_cdp(cdp_url)
            except Exception as exc:
                raise RuntimeError(
                    "Could not connect to Chrome for claude.ai. "
                    "Quit Chrome completely, then in another terminal run:\n"
                    "  ./story-agent/start-debug-browser.sh\n"
                    "Log into https://claude.ai/new if needed, then re-run the agent."
                ) from exc
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
        else:
            log("Launching Chrome with your profile (quit other Chrome windows first)")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(chrome_user_data),
                channel="chrome",
                headless=False,
                args=[
                    f"--profile-directory={profile_directory}",
                    "--disable-blink-features=AutomationControlled",
                ],
                viewport={"width": 1440, "height": 900},
            )
            page = context.pages[0] if context.pages else context.new_page()

        page.goto("https://claude.ai/new", wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(3000)

        if "login" in page.url.lower() or page.locator("text=Continue with Google").count():
            log("Not logged in — log into claude.ai in the opened Chrome window.")
            log("Press Enter here once the chat composer is visible...")
            input()

        composer = find_composer(page)
        composer.click()
        page.evaluate(
            """async (text) => {
                await navigator.clipboard.writeText(text);
            }""",
            prompt,
        )
        page.keyboard.press("Meta+V" if sys.platform == "darwin" else "Control+V")
        page.wait_for_timeout(1500)

        send = page.locator('button[aria-label="Send message"], button[data-testid="send-button"]').first
        if send.count() and send.is_enabled():
            send.click()
        else:
            page.keyboard.press("Enter")

        log("Waiting for Claude to finish writing...")
        wait_for_generation_done(page, timeout_seconds=timeout_seconds)

        response_text = extract_last_assistant_message(page)
        if not response_text.strip():
            raise RuntimeError("Could not read Claude response from the page.")

        if not cdp_url:
            context.close()
        else:
            page.close()

        return response_text


def find_composer(page):
    selectors = [
        '[data-testid="chat-input"]',
        'div[contenteditable="true"][role="textbox"]',
        'div.ProseMirror[contenteditable="true"]',
        'div[contenteditable="true"]',
        '[role="textbox"]',
    ]
    for sel in selectors:
        loc = page.locator(sel).last
        if loc.count():
            loc.wait_for(state="visible", timeout=60_000)
            return loc
    raise RuntimeError("Could not find Claude chat input. Update selectors or log in manually.")


def wait_for_generation_done(page, *, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    stable_checks = 0
    last_len = 0

    while time.time() < deadline:
        stop_visible = page.locator(
            'button[aria-label="Stop response"], button:has-text("Stop")'
        ).count() > 0
        if stop_visible:
            page.wait_for_timeout(2000)
            continue

        current = extract_last_assistant_message(page)
        current_len = len(current)
        if current_len > 200 and current_len == last_len:
            stable_checks += 1
            if stable_checks >= 3:
                return
        else:
            stable_checks = 0
            last_len = current_len

        page.wait_for_timeout(2000)

    raise TimeoutError(f"Timed out after {timeout_seconds}s waiting for Claude response.")


def extract_last_assistant_message(page) -> str:
    selectors = [
        '[data-testid="assistant-message"]',
        '[data-testid="assistant-message-content"]',
        'div.font-claude-message',
        'div[class*="assistant"]',
    ]
    for sel in selectors:
        loc = page.locator(sel)
        if loc.count():
            return loc.last.inner_text()

    # Fallback: grab the largest recent text block on the page.
    return page.evaluate(
        """() => {
            const blocks = [...document.querySelectorAll('div, article, section')]
              .map(el => (el.innerText || '').trim())
              .filter(t => t.length > 500)
              .sort((a, b) => b.length - a.length);
            return blocks[0] || '';
        }"""
    )



def save_pipeline_outputs(
    output_dir: Path,
    *,
    slug: str,
    title: str,
    video_id: str,
    youtube_url: str,
    story_type: str,
    research_dir: Path,
    source_chars: int,
    target_chars: int,
    prompt: str,
    raw_response: str,
    story_text: str,
    video_count: int,
    duration_minutes: int | None = None,
    prompt_file: Path | None = None,
    research_source: str = "transcripts",
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    story_path = output_dir / "FULL_STORY.txt"
    story_path.write_text(story_text, encoding="utf-8")

    meta = {
        "title": title,
        "slug": slug,
        "video_id": video_id,
        "youtube_url": youtube_url,
        "story_type": story_type,
        "research_dir": str(research_dir),
        "transcript_sources": video_count,
        "source_characters": source_chars,
        "target_characters": target_chars,
        "output_characters": len(story_text),
        "duration_minutes": duration_minutes,
        "research_source": research_source,
        "prompt_file": str(prompt_file or PROMPTS[story_type]),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (output_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "raw.md").write_text(raw_response, encoding="utf-8")
    (output_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    pointers_src = research_dir / "story_pointers.txt"
    if pointers_src.is_file():
        shutil.copy2(pointers_src, output_dir / "story_pointers.txt")

    return story_path


def call_llm(
    prompt: str,
    *,
    provider: str,
    mode: str,
    model: str,
    max_tokens: int,
    browser: str,
    firefox_profile: str,
    cdp_url: str | None,
    timeout: int,
    claude_code_model: str | None,
) -> str:
    if provider == "chatgpt":
        raise RuntimeError("ChatGPT provider not configured in this build. Use --provider claude.")

    if mode == "api":
        return call_claude_api(prompt, model=model, max_tokens=max_tokens)
    if mode == "browser":
        use_cdp = browser == "cdp"
        return call_claude_browser(
            prompt,
            cdp_url=cdp_url if use_cdp else None,
            chrome_user_data=DEFAULT_CHROME_USER_DATA,
            profile_directory=firefox_profile or DEFAULT_FIREFOX_PROFILE,
            timeout_seconds=timeout,
        )
    return call_claude_code(prompt, model=claude_code_model, timeout_seconds=timeout)
