#!/usr/bin/env python3
"""Fetch YouTube transcript into library/<category>/stories/ + metadata/videos.json."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi

LIBRARY = Path(__file__).resolve().parent
CATEGORIES = ("general", "crime")


def category_paths(category: str) -> tuple[Path, Path]:
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    root = LIBRARY / category
    return root / "stories", root / "metadata" / "videos.json"


def extract_video_id(url_or_id: str) -> str:
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def slug_title(title: str) -> str:
    title = re.sub(r"\s*\|\s*2D Animation\s*$", "", title, flags=re.I).strip()
    title = re.sub(r'[<>:"/\\|?*]', "", title)
    return re.sub(r"\s+", " ", title).strip()


def channel_handle_from_url(url: str) -> str | None:
    match = re.search(r"youtube\.com/(@[\w.-]+)", url)
    return match.group(1) if match else None


def normalize_channel_url(url: str) -> str:
    url = url.rstrip("/")
    if "/videos" not in url and "/@" in url:
        return f"{url}/videos"
    return url


def fetch_yt_metadata(video_id: str) -> dict:
    try:
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--dump-json", "--no-download",
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        data = json.loads(subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=60))
        return {
            "video_id": data.get("id"),
            "title": data.get("title"),
            "channel": data.get("channel"),
            "channel_id": data.get("channel_id"),
            "channel_url": data.get("channel_url"),
            "youtube_url": data.get("webpage_url"),
            "upload_date": data.get("upload_date"),
            "duration_seconds": data.get("duration"),
            "view_count": data.get("view_count"),
            "like_count": data.get("like_count"),
            "comment_count": data.get("comment_count"),
            "description": data.get("description"),
            "tags": data.get("tags"),
            "thumbnail": data.get("thumbnail"),
        }
    except Exception as exc:
        return {
            "video_id": video_id,
            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
            "fetch_error": str(exc),
        }


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> tuple[list, str]:
    api = YouTubeTranscriptApi()
    langs = languages or ["hi", "en"]
    result = api.fetch(video_id, languages=langs)
    plain = " ".join(segment.text for segment in result)
    return result, plain


def load_metadata(metadata_file: Path) -> list[dict]:
    if metadata_file.exists():
        return json.loads(metadata_file.read_text(encoding="utf-8"))
    return []


def save_metadata(metadata_file: Path, entries: list[dict]) -> None:
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def upsert_metadata(metadata_file: Path, entry: dict) -> None:
    entries = load_metadata(metadata_file)
    entries = [e for e in entries if e.get("video_id") != entry.get("video_id")]
    entries.append(entry)
    entries.sort(key=lambda e: e.get("view_count") or 0, reverse=True)
    save_metadata(metadata_file, entries)


def save_story(
    stories_dir: Path,
    metadata_file: Path,
    video_id: str,
    plain: str,
    result,
    yt_meta: dict,
) -> Path:
    stories_dir.mkdir(parents=True, exist_ok=True)
    title = yt_meta.get("title") or video_id
    story_name = slug_title(title)
    story_path = stories_dir / f"{story_name}.txt"
    story_path.write_text(plain, encoding="utf-8")

    yt_meta["story_filename"] = f"{story_name}.txt"
    yt_meta["transcript_characters"] = len(plain)
    yt_meta["transcript_words"] = len(plain.split())
    yt_meta["transcript_segments"] = len(result)
    upsert_metadata(metadata_file, yt_meta)
    return story_path


def fetch_channel_video_ids(channel_url: str, scan_limit: int) -> list[tuple[str, str]]:
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist", f"--playlist-end={scan_limit}",
        "--print", "%(id)s|%(title)s",
        channel_url,
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
    videos = []
    for line in out.strip().splitlines():
        if "|" not in line:
            continue
        vid, title = line.split("|", 1)
        videos.append((vid, title))
    return videos


def fetch_channel_top_by_views(
    channel_url: str,
    *,
    min_views: int,
    top: int,
    scan_limit: int,
) -> list[tuple[str, str, int]]:
    channel_url = normalize_channel_url(channel_url)
    candidates = fetch_channel_video_ids(channel_url, scan_limit)
    ranked: list[tuple[str, str, int]] = []

    for vid, title in candidates:
        meta = fetch_yt_metadata(vid)
        views = meta.get("view_count") or 0
        if views >= min_views:
            ranked.append((vid, meta.get("title") or title, views))

    ranked.sort(key=lambda item: item[2], reverse=True)
    return ranked[:top]


def fetch_channel_videos(channel_url: str, limit: int) -> list[tuple[str, str]]:
    channel_url = normalize_channel_url(channel_url)
    return fetch_channel_video_ids(channel_url, limit)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch YouTube transcript into library/<category>/")
    parser.add_argument("url", nargs="?", help="YouTube URL, video ID, or channel /videos URL")
    parser.add_argument("--category", choices=CATEGORIES, default="general",
                        help="Library category folder (default: general)")
    parser.add_argument("--channel", help="Channel URL (e.g. https://www.youtube.com/@anidoc28/videos)")
    parser.add_argument("--limit", type=int, default=5, help="Number of channel videos to fetch (default: 5)")
    parser.add_argument("--min-views", type=int, default=0,
                        help="Only include channel videos with at least this many views")
    parser.add_argument("--top", type=int, default=0,
                        help="With --min-views, fetch top N videos by view count (0 = use --limit order)")
    parser.add_argument("--scan-limit", type=int, default=200,
                        help="Max channel videos to scan when using --min-views (default: 200)")
    parser.add_argument("--lang", nargs="+", default=["hi", "en"], help="Transcript languages")
    args = parser.parse_args()

    stories_dir, metadata_file = category_paths(args.category)
    channel_url = args.channel or args.url
    channel_handle = channel_handle_from_url(channel_url) if channel_url else None

    targets: list[tuple[str, str | None, int | None]] = []

    is_channel = bool(args.channel) or (
        args.url and ("/@" in args.url or "/channel/" in args.url or "/videos" in args.url)
    )

    if is_channel and channel_url:
        if args.min_views > 0 and args.top > 0:
            for vid, title, views in fetch_channel_top_by_views(
                channel_url,
                min_views=args.min_views,
                top=args.top,
                scan_limit=args.scan_limit,
            ):
                targets.append((vid, title, views))
            print(f"Selected top {len(targets)} videos with >= {args.min_views:,} views")
        else:
            for vid, title in fetch_channel_videos(channel_url, args.limit):
                targets.append((vid, title, None))
    elif args.url:
        targets.append((extract_video_id(args.url), None, None))
    else:
        parser.error("Provide a video URL/ID or --channel URL")

    for i, (video_id, channel_title, preset_views) in enumerate(targets, 1):
        try:
            yt_meta = fetch_yt_metadata(video_id)
            if channel_title and not yt_meta.get("title"):
                yt_meta["title"] = channel_title
            if channel_handle:
                yt_meta["channel_handle"] = channel_handle
            yt_meta["channel_rank"] = i
            if preset_views is not None:
                yt_meta["view_count"] = preset_views
            result, plain = fetch_transcript(video_id, args.lang)
            story_path = save_story(stories_dir, metadata_file, video_id, plain, result, yt_meta)
            views = yt_meta.get("view_count") or 0
            print(f"[{i}/{len(targets)}] {story_path.name} ({len(plain)} chars, {views:,} views)")
        except Exception as exc:
            print(f"[{i}/{len(targets)}] {video_id} FAILED: {exc}", file=sys.stderr)

    print(f"Metadata updated: {metadata_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
