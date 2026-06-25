#!/usr/bin/env python3
"""
Unified story agent: research YouTube transcripts + generate story by type.

Queue file (default queue.txt):
  URL,related_count,story_type[,folder_name]

Or single video:
  --video-url URL --type crime --related 25
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from library.fetch_youtube_transcript import extract_video_id, fetch_yt_metadata  # noqa: E402
from library import story_generate as gen  # noqa: E402
from library import story_research as research  # noqa: E402

DEFAULT_QUEUE = AGENT_DIR / "queue.txt"
DEFAULT_OUTPUT = AGENT_DIR / "output"
STATE_FILE = "processed.json"


def log(msg: str) -> None:
    print(f"[story-agent] {msg}", flush=True)


@dataclass
class StoryJob:
    url: str
    related: int
    story_type: str
    folder_name: str | None = None


def parse_queue_line(line: str, line_no: int) -> StoryJob | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    parts = [p.strip() for p in stripped.split(",")]
    if len(parts) < 3:
        raise ValueError(
            f"Line {line_no}: expected URL,related_count,story_type — got: {line!r}"
        )

    url = parts[0]
    if not url.startswith("http") and len(url) != 11:
        raise ValueError(f"Line {line_no}: invalid YouTube URL: {url!r}")

    try:
        related = int(parts[1])
    except ValueError as exc:
        raise ValueError(f"Line {line_no}: related_count must be an integer") from exc
    if related < 0:
        raise ValueError(f"Line {line_no}: related_count must be >= 0")

    story_type = gen.normalize_story_type(parts[2])
    folder_name = parts[3] if len(parts) > 3 else None
    return StoryJob(url=url, related=related, story_type=story_type, folder_name=folder_name)


def load_queue(path: Path) -> list[StoryJob]:
    if not path.exists():
        raise FileNotFoundError(f"Queue file not found: {path}")
    jobs: list[StoryJob] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        job = parse_queue_line(line, i)
        if job:
            jobs.append(job)
    return jobs


def load_state(output_dir: Path) -> dict:
    path = output_dir / STATE_FILE
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"processed": {}}


def save_state(output_dir: Path, state: dict) -> None:
    (output_dir / STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def resolve_research_dir(job: StoryJob, args, seed_title: str) -> Path:
    if args.research_dir:
        research_dir = args.research_dir
    else:
        slug_hint = job.folder_name or research.folder_slug_from_title(seed_title)
        research_dir = args.research_dir_base / slug_hint
    if not research_dir.exists():
        raise FileNotFoundError(
            f"Research folder not found: {research_dir}. "
            "Run without --generate-only first, or pass --research-dir."
        )
    return research_dir


def process_job(job: StoryJob, *, args, state: dict) -> None:
    video_id = extract_video_id(job.url)
    state_key = f"{video_id}:{job.story_type}"

    if state_key in state["processed"] and not args.force:
        info = state["processed"][state_key]
        log(
            f"Skipping {video_id} ({job.story_type}) — already done as {info.get('slug')}. "
            "Use --force to redo."
        )
        return

    seed_meta = fetch_yt_metadata(video_id)
    seed_title = seed_meta.get("title") or video_id

    log(f"=== {seed_title}")
    log(f"Type: {job.story_type} | Related videos: {job.related}")

    if args.generate_only:
        log("Generate-only — using existing research")
        research_dir = resolve_research_dir(job, args, seed_title)
    else:
        log("Step 1/2 — downloading transcripts")
        research_dir = research.run_research(
            job.url,
            output_base=args.research_dir_base,
            folder_name=job.folder_name,
            related_count=job.related,
            search_limit=max(job.related * 2, 25),
            min_views=args.min_views,
            languages=args.lang,
            force=args.force,
        )

    if args.research_only:
        log(f"Research complete: {research_dir}")
        return

    combined, source_chars, used_videos = research.combine_transcripts(research_dir)
    target_chars = source_chars + args.extra_chars
    slug = gen.story_slug(seed_title)
    prompt_path = Path(args.prompt) if args.prompt else gen.PROMPTS[job.story_type]

    log(f"Combined source: {source_chars:,} chars from {len(used_videos)} transcript(s)")
    log(f"Target length: {target_chars:,} chars (+{args.extra_chars:,})")

    prompt = gen.build_prompt_for_type(job.story_type, prompt_path, combined, target_chars)
    story_dir = args.output_dir / job.story_type / research.research_folder_slug(research_dir)

    if args.prepare_only:
        story_dir.mkdir(parents=True, exist_ok=True)
        out = story_dir / "prompt.txt"
        out.write_text(prompt, encoding="utf-8")
        log(f"Prompt saved: {out}")
        return

    log("Step 2/2 — generating story")
    raw_response = gen.call_llm(
        prompt,
        provider=args.provider,
        mode=args.mode,
        model=args.model,
        max_tokens=args.max_tokens,
        browser=args.browser,
        firefox_profile=args.firefox_profile,
        cdp_url=args.cdp_url,
        timeout=args.timeout,
        claude_code_model=args.claude_code_model,
    )
    story_text = gen.extract_full_script(raw_response)

    story_path = gen.save_pipeline_outputs(
        story_dir,
        slug=slug,
        title=seed_title,
        video_id=video_id,
        youtube_url=job.url,
        story_type=job.story_type,
        research_dir=research_dir,
        source_chars=source_chars,
        target_chars=target_chars,
        prompt=prompt,
        raw_response=raw_response,
        story_text=story_text,
        video_count=len(used_videos),
    )

    state["processed"][state_key] = {
        "slug": slug,
        "story_type": job.story_type,
        "title": seed_title,
        "research_dir": str(research_dir),
        "output_dir": str(story_dir),
        "source_characters": source_chars,
        "output_characters": len(story_text),
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    save_state(args.output_dir, state)

    log(f"Story saved ({len(story_text):,} chars): {story_path}")
    log(f"Research: {research_dir}")


def show_status(output_dir: Path) -> int:
    state = load_state(output_dir)
    processed = state.get("processed", {})
    print(f"Output dir: {output_dir}")
    print(f"Processed: {len(processed)}")
    for key, info in processed.items():
        print(
            f"  - {info.get('story_type', '?')}/{info.get('slug', '?')} "
            f"| {info.get('title', key)[:60]} "
            f"| source={info.get('source_characters', '?')} "
            f"| output={info.get('output_characters', '?')}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified story agent: YouTube research → story by type"
    )
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE), help="Queue file path")
    parser.add_argument("--video-url", help="Single video URL (instead of queue)")
    parser.add_argument("--type", dest="story_type", help="Story type for --video-url")
    parser.add_argument("--related", type=int, default=5, help="Related videos for --video-url")
    parser.add_argument("--folder", help="Research folder name override")
    parser.add_argument("--research-dir-base", type=Path, default=research.DEFAULT_RESEARCH_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--research-dir", type=Path, help="Existing research (with --generate-only)")
    parser.add_argument("--extra-chars", type=int, default=1000)
    parser.add_argument("--prompt", help="Override master prompt file")
    parser.add_argument("--lang", nargs="+", default=["hi", "en"])
    parser.add_argument("--min-views", type=int, default=10_000)
    parser.add_argument("--provider", choices=("claude", "chatgpt"), default="claude")
    parser.add_argument("--mode", choices=("claude-code", "browser", "api"), default="claude-code")
    parser.add_argument("--browser", choices=("firefox", "cdp"), default="firefox")
    parser.add_argument("--firefox-profile", default=gen.DEFAULT_FIREFOX_PROFILE)
    parser.add_argument("--cdp-url")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--claude-code-model", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-tokens", type=int, default=64000)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--research-only", action="store_true")
    parser.add_argument("--generate-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--status", action="store_true")
    return parser


def main() -> int:
    gen.load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.status:
        return show_status(args.output_dir)

    if args.model is None:
        args.model = "gpt-4.1" if args.provider == "chatgpt" else "claude-sonnet-4-20250514"

    if args.generate_only and args.research_only:
        parser.error("--generate-only and --research-only cannot be used together")

    if args.video_url:
        if not args.story_type:
            parser.error("--video-url requires --type (crime|general|english|god)")
        jobs = [
            StoryJob(
                url=args.video_url,
                related=args.related,
                story_type=gen.normalize_story_type(args.story_type),
                folder_name=args.folder,
            )
        ]
    else:
        jobs = load_queue(Path(args.queue))
        if not jobs:
            log(f"No active entries in {args.queue}")
            return 1

    state = load_state(args.output_dir)
    log(f"Processing {len(jobs)} job(s)")

    failed = 0
    for i, job in enumerate(jobs, 1):
        log(f"\n--- [{i}/{len(jobs)}] {job.url}")
        try:
            process_job(job, args=args, state=state)
        except Exception as exc:
            log(f"FAILED: {exc}")
            failed += 1
            if len(jobs) == 1:
                return 1

    if failed:
        log(f"Finished with {failed} failure(s)")
        return 1
    log("All jobs complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
