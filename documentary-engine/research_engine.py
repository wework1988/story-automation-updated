#!/usr/bin/env python3
"""YouTube research engine — channel-first transcripts for story generation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE_ROOT))

from src.youtube_research import extract_video_id, fetch_metadata, run_channel_first_research  # noqa: E402


DEFAULT_STORAGE = ENGINE_ROOT / "storage"
DEFAULT_QUEUE = ENGINE_ROOT / "queue.txt"


def folder_slug_from_title(title: str, video_id: str) -> str:
    title = re.sub(r"[#@]", "", title)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        slug = video_id
    return slug[:80]


def parse_queue_line(line: str, line_no: int) -> str | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 1:
        return None
    url = parts[0]
    if not url.startswith("http"):
        raise ValueError(f"queue.txt line {line_no}: expected YouTube URL, got {url!r}")
    return url


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="YouTube research engine — search priority channels, download transcripts, combine"
    )
    p.add_argument("--url", help="Seed YouTube URL (topic anchor)")
    p.add_argument("--folder", help="Output folder name under storage/")
    p.add_argument("--queue", default=str(DEFAULT_QUEUE), help="Queue file: one URL per line")
    p.add_argument("--count", type=int, default=4, help="Target number of videos (default: 4)")
    p.add_argument("--min-channel", type=int, default=3, help="Min priority-channel hits to skip fallback (default: 3)")
    p.add_argument("--min-views", type=int, default=10_000, help="Minimum view count")
    p.add_argument(
        "--min-content-relevance",
        type=float,
        default=0.50,
        help="Minimum transcript-level same-story overlap with the seed video (default: 0.50)",
    )
    p.add_argument(
        "--max-queries",
        type=int,
        default=3,
        help="How many context-derived search queries to run per channel (default: 3)",
    )
    p.add_argument("--storage", type=Path, default=DEFAULT_STORAGE, help="Storage root directory")
    return p


def run_one(url: str, args: argparse.Namespace) -> Path:
    seed_id = extract_video_id(url)
    seed_meta = fetch_metadata(seed_id)
    folder = args.folder or folder_slug_from_title(seed_meta.get("title") or seed_id, seed_id)
    output_dir = args.storage / folder

    return run_channel_first_research(
        url,
        output_dir=output_dir,
        target_count=args.count,
        min_channel_count=args.min_channel,
        min_views=args.min_views,
        min_content_relevance=args.min_content_relevance,
        max_queries=args.max_queries,
    )


def main() -> int:
    args = build_parser().parse_args()

    if args.url:
        urls = [args.url]
    else:
        queue_path = Path(args.queue)
        if not queue_path.exists():
            print(f"Provide --url or create {queue_path}", file=sys.stderr)
            return 1
        urls = []
        for i, line in enumerate(queue_path.read_text(encoding="utf-8").splitlines(), 1):
            url = parse_queue_line(line, i)
            if url:
                urls.append(url)
        if not urls:
            print(f"No URLs in {queue_path}", file=sys.stderr)
            return 1

    failed = 0
    for i, url in enumerate(urls, 1):
        print(f"\n--- [{i}/{len(urls)}] {url}")
        try:
            out = run_one(url, args)
            print(f"Research saved: {out}")
        except Exception as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
