"""Extract per-transcript story pointers via DeepSeek and merge into one ledger."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from library.deepseek_client import DeepSeekClient, load_deepseek_settings
from library.story_research import load_videos_json

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BULLET_PROMPT = REPO_ROOT / "bullet-pointers.txt"
RAW_DIRNAME = "bullet_extract_raw"
COMBINED_FILENAME = "story_pointers.txt"
META_FILENAME = "story_pointers-meta.json"

LEDGER_HEADER = """══════════════════════════════════════════════════════════════════
STORY POINTER LEDGER — SOLE FACTUAL SOURCE (NO RAW TRANSCRIPTS)
══════════════════════════════════════════════════════════════════
Use ONLY the story pointers below as research input for the master story prompt.
Do NOT invent details beyond these pointers. Do NOT request raw transcripts.

TOPIC: {topic}
SOURCES IN LEDGER: {source_count}
GENERATED AT: {generated_at}

── PER-SOURCE STORY POINTERS ──
"""

POINTER_INPUT_PREAMBLE = """INPUT TYPE: PRE-EXTRACTED STORY POINTERS (not raw YouTube captions)
Each block below is one source video reduced to 20–25 factual pointers (Explains / How).
Run the TRANSCRIPT MERGE PROTOCOL on these pointers only. Facts may repeat across sources —
merge duplicates, prefer CONFIRMED when 2+ sources agree.

"""


def log(msg: str) -> None:
    print(f"[pointers] {msg}", flush=True)


def load_bullet_prompt(path: Path | None = None) -> str:
    prompt_path = path or DEFAULT_BULLET_PROMPT
    if not prompt_path.is_file():
        raise FileNotFoundError(f"Bullet pointer prompt not found: {prompt_path}")
    text = prompt_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Bullet pointer prompt is empty: {prompt_path}")
    return text


def _transcript_path(research_dir: Path, entry: dict) -> Path | None:
    filename = entry.get("filename")
    if not filename:
        return None
    path = research_dir / filename
    return path if path.exists() else None


def _raw_pointer_path(research_dir: Path, video_id: str) -> Path:
    return research_dir / RAW_DIRNAME / f"{video_id}.txt"


def extract_pointers_for_source(
    client: DeepSeekClient,
    *,
    bullet_instructions: str,
    video_id: str,
    title: str,
    youtube_url: str,
    transcript: str,
    max_tokens: int,
) -> str:
    user_prompt = (
        f"Extract story pointers from the transcript below.\n\n"
        f"VIDEO ID: {video_id}\n"
        f"TITLE: {title}\n"
        f"URL: {youtube_url}\n\n"
        f"TRANSCRIPT:\n{transcript.strip()}\n"
    )
    raw = client.chat(
        system_prompt=bullet_instructions,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        label=f"pointers/{video_id}",
        thinking=False,
        temperature=0.2,
    )
    return raw.strip()


def _wrap_source_block(video_id: str, title: str, body: str) -> str:
    return f"═══ SOURCE: {video_id} — {title} ═══\n\n{body.strip()}\n"


def combine_pointer_blocks(blocks: list[str], *, topic: str) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    header = LEDGER_HEADER.format(
        topic=topic,
        source_count=len(blocks),
        generated_at=generated_at,
    )
    return header + "\n".join(blocks)


def run_bullet_extraction(
    research_dir: Path,
    *,
    topic: str | None = None,
    bullet_prompt_path: Path | None = None,
    deepseek_config: Path | None = None,
    force: bool = False,
) -> Path:
    """Extract pointers for each transcript; write story_pointers.txt."""
    videos_json = research_dir / "videos.json"
    if not videos_json.exists():
        raise FileNotFoundError(f"No videos.json in {research_dir}")

    videos = load_videos_json(videos_json)
    if not videos:
        raise RuntimeError(f"No videos listed in {videos_json}")

    meta_path = research_dir / "research-meta.json"
    if topic is None and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        topic = meta.get("seed_title") or meta.get("search_query") or research_dir.name
    topic = topic or research_dir.name

    combined_path = research_dir / COMBINED_FILENAME
    raw_dir = research_dir / RAW_DIRNAME
    raw_dir.mkdir(parents=True, exist_ok=True)

    if combined_path.exists() and not force:
        log(f"Reusing existing {COMBINED_FILENAME} (use --force to redo)")
        return combined_path

    bullet_instructions = load_bullet_prompt(bullet_prompt_path)
    settings = load_deepseek_settings(deepseek_config)
    client = DeepSeekClient(settings)

    blocks: list[str] = []
    extracted: list[dict] = []

    for entry in sorted(
        videos, key=lambda v: (v.get("role") != "seed", -(v.get("view_count") or 0))
    ):
        video_id = entry.get("video_id")
        if not video_id:
            continue
        path = _transcript_path(research_dir, entry)
        if path is None:
            log(f"skip missing transcript for {video_id}")
            continue

        raw_path = _raw_pointer_path(research_dir, video_id)
        if raw_path.exists() and not force:
            body = raw_path.read_text(encoding="utf-8").strip()
            log(f"reusing {raw_path.name}")
        else:
            transcript = path.read_text(encoding="utf-8").strip()
            if not transcript:
                log(f"skip empty transcript: {path.name}")
                continue
            title = entry.get("title") or video_id
            url = entry.get("youtube_url") or f"https://www.youtube.com/watch?v={video_id}"
            log(f"extracting pointers: {title[:70]}…")
            body = extract_pointers_for_source(
                client,
                bullet_instructions=bullet_instructions,
                video_id=video_id,
                title=title,
                youtube_url=url,
                transcript=transcript,
                max_tokens=settings.max_tokens_bullets,
            )
            raw_path.write_text(body, encoding="utf-8")

        title = entry.get("title") or video_id
        blocks.append(_wrap_source_block(video_id, title, body))
        extracted.append(
            {
                "video_id": video_id,
                "title": title,
                "role": entry.get("role"),
                "raw_file": str(raw_path.relative_to(research_dir)),
                "pointer_characters": len(body),
            }
        )

    if not blocks:
        raise RuntimeError(f"No pointer blocks produced in {research_dir}")

    combined = combine_pointer_blocks(blocks, topic=topic)
    combined_path.write_text(combined, encoding="utf-8")

    (research_dir / META_FILENAME).write_text(
        json.dumps(
            {
                "topic": topic,
                "source_count": len(blocks),
                "sources": extracted,
                "combined_file": COMBINED_FILENAME,
                "bullet_prompt": str(bullet_prompt_path or DEFAULT_BULLET_PROMPT),
                "deepseek_model": settings.model,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    log(f"Saved {COMBINED_FILENAME} ({len(combined):,} chars, {len(blocks)} sources)")
    return combined_path


def load_combined_pointers(research_dir: Path) -> str:
    path = research_dir / COMBINED_FILENAME
    if not path.exists():
        raise FileNotFoundError(
            f"{COMBINED_FILENAME} not found in {research_dir}. "
            "Run bullet extraction first (--pointers-only or full pipeline with --use-bullet-pointers)."
        )
    return path.read_text(encoding="utf-8").strip()


def pointer_source_for_prompt(research_dir: Path) -> tuple[str, int]:
    """Return ledger text (with preamble) and character count for story prompt."""
    ledger = load_combined_pointers(research_dir)
    text = POINTER_INPUT_PREAMBLE + ledger
    return text, len(text)


def count_pointers_in_ledger(text: str) -> int:
    return len(re.findall(r"POINTER\s+\d+", text, flags=re.IGNORECASE))
