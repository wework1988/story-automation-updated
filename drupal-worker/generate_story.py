#!/usr/bin/env python3
"""CMS Pipeline 1: YouTube URLs → bullet pointers → v3 master → FULL_STORY."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

WORKER_DIR = Path(__file__).resolve().parent
REPO_ROOT = WORKER_DIR.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(WORKER_DIR))

from cms_local import (  # noqa: E402
    build_story_meta,
    find_cms_dir_by_node_id,
    load_local_story,
    sync_outputs_to_cms,
)
from drupal_client import fetch_story, push_story_outputs  # noqa: E402
from library import story_generate as gen  # noqa: E402
from library.story_pipeline import StoryPipelineInput, run_story_pipeline  # noqa: E402


def log(msg: str) -> None:
    print(f"[drupal-worker] {msg}", flush=True)


def resolve_story(*, node_id: str | None, cms_dir: Path | None, from_drupal: bool):
    if from_drupal:
        if not node_id:
            raise ValueError("--node-id required with --from-drupal")
        story = fetch_story(node_id)
        if len(story.youtube_urls) < 2:
            raise ValueError(
                f"Story {node_id} needs 2+ YouTube URLs in field_youtube_urls"
            )
        folder_name = f"node-{story.id}-research"
        return (
            story.youtube_urls[0],
            story.youtube_urls[1:],
            gen.normalize_story_type(story.story_type),
            story.duration_minutes,
            folder_name,
            None,
            story.id,
            story.title,
        )

    if cms_dir:
        local = load_local_story(cms_dir)
    elif node_id:
        found = find_cms_dir_by_node_id(node_id)
        if not found:
            raise FileNotFoundError(
                f"No cms-generate-stories folder with meta/drupal-node-id.txt = {node_id}"
            )
        local = load_local_story(found)
        cms_dir = found
    else:
        raise ValueError("Pass --node-id and/or --cms-dir, or --from-drupal --node-id")

    if len(local.youtube_urls) < 2:
        raise ValueError(
            f"Add URLs to {local.cms_dir / 'meta' / 'youtube-urls.txt'} (one per line, 2+)"
        )
    folder_slug = local.cms_dir.name.replace("-", " ")  # use cms folder basename
    folder_name = f"{local.cms_dir.name}-research"
    return (
        local.youtube_urls[0],
        local.youtube_urls[1:],
        gen.normalize_story_type(local.story_type),
        local.duration_minutes,
        folder_name,
        cms_dir,
        local.node_id,
        local.title,
    )


def main() -> int:
    gen.load_dotenv()
    parser = argparse.ArgumentParser(
        description="Generate story from CMS YouTube URLs (bullet-pointer pipeline)"
    )
    parser.add_argument("--node-id", help="Drupal node ID (e.g. 127)")
    parser.add_argument(
        "--cms-dir",
        type=Path,
        help="cms-generate-stories/.../127-my-story folder",
    )
    parser.add_argument(
        "--from-drupal",
        action="store_true",
        help="Fetch story from Drupal API (DRUPAL_BASE_URL + DRUPAL_API_KEY)",
    )
    parser.add_argument("--duration", type=int, help="Override duration in minutes")
    parser.add_argument("--type", dest="story_type", help="Override story type")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--research-only", action="store_true")
    parser.add_argument("--pointers-only", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument(
        "--mode",
        choices=("api", "browser", "claude-code"),
        default="api",
        help="LLM mode (default: api for CMS worker)",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-tokens", type=int, default=64000)
    args = parser.parse_args()

    seed_url, related_urls, story_type, duration, folder_name, cms_dir, node_id, title = (
        resolve_story(
            node_id=args.node_id,
            cms_dir=args.cms_dir,
            from_drupal=args.from_drupal,
        )
    )
    if args.story_type:
        story_type = gen.normalize_story_type(args.story_type)
    if args.duration:
        duration = args.duration

    log(f"Node {node_id or '?'} | {title or seed_url}")
    log(f"Type: {story_type} | Duration: {duration} min | Sources: {1 + len(related_urls)}")

    inp = StoryPipelineInput(
        seed_url=seed_url,
        related_urls=related_urls,
        story_type=story_type,
        duration_minutes=duration,
        folder_name=folder_name,
        force=args.force,
        llm_mode=args.mode,
        llm_model=args.model,
        max_tokens=args.max_tokens,
    )

    result = run_story_pipeline(
        inp,
        skip_download=False,
        research_only=args.research_only,
        pointers_only=args.pointers_only,
        prepare_only=args.prepare_only,
        skip_llm=args.research_only or args.pointers_only or args.prepare_only,
    )

    if args.research_only:
        log(f"Research complete: {result.research_dir}")
        return 0
    if args.pointers_only:
        log(f"Pointers complete: {result.research_dir / 'story_pointers.txt'}")
        return 0
    if args.prepare_only:
        log(f"Prompt saved: {result.story_dir / 'prompt.txt'}")
        return 0

    story_meta = build_story_meta(
        len(result.story_text),
        result.target_chars,
        pipeline="bullet-pointers-v3",
    )

    if cms_dir:
        sync_outputs_to_cms(
            cms_dir,
            research_dir=result.research_dir,
            story_dir=result.story_dir,
            story_meta=story_meta,
        )
        log(f"Synced to CMS folder: {cms_dir / 'script' / 'FULL_STORY.txt'}")

    if args.from_drupal and node_id:
        push_story_outputs(
            node_id,
            full_story=result.story_text,
            story_meta=story_meta,
        )
        log(f"Pushed to Drupal story {node_id}")

    log(f"Done ({len(result.story_text):,} chars): {result.story_dir / 'FULL_STORY.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
