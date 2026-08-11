#!/usr/bin/env python3
"""Fetch YouTube transcript into library/<category>/stories/ + metadata/videos.json."""

from __future__ import annotations

import argparse
import json
import os
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


def _parse_vtt_to_plain(vtt_text: str) -> str:
    lines: list[str] = []
    for line in vtt_text.splitlines():
        line = line.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if re.match(r"^\d+$", line):
            continue
        if "-->" in line:
            continue
        if line.startswith("NOTE"):
            continue
        lines.append(line)
    # de-dupe consecutive identical lines (common in auto-captions)
    deduped: list[str] = []
    for line in lines:
        if not deduped or deduped[-1] != line:
            deduped.append(line)
    return " ".join(deduped)


def youtube_cookies_path() -> str | None:
    """Optional Netscape cookies.txt exported from a logged-in browser session."""
    raw = (os.environ.get("YOUTUBE_COOKIES_FILE") or "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    return str(path) if path.is_file() else None


def youtube_cookies_browser() -> str | None:
    """
    Browser name for yt-dlp --cookies-from-browser (e.g. firefox, chrome, chromium).
    Reads YOUTUBE_COOKIES_BROWSER. Use firefox when logged into YouTube in Mozilla.
    """
    raw = (os.environ.get("YOUTUBE_COOKIES_BROWSER") or "").strip()
    return raw if raw else None


def youtube_has_auth_cookies() -> bool:
    return bool(youtube_cookies_path() or youtube_cookies_browser())


def ytdlp_cookie_cli_args() -> list[str]:
    """Prefer live browser profile (firefox) over a static cookies.txt file."""
    browser = youtube_cookies_browser()
    if browser:
        return ["--cookies-from-browser", browser]
    path = youtube_cookies_path()
    if path:
        return ["--cookies", path]
    return []


def ytdlp_subprocess_env() -> dict[str, str]:
    """Ensure deno/node are on PATH for yt-dlp JS challenge solving."""
    env = os.environ.copy()
    extra = "/opt/homebrew/bin:/usr/local/bin"
    env["PATH"] = extra + os.pathsep + env.get("PATH", "")
    return env


# Avoid web client subtitle PO-token requirement (see yt-dlp issue #13075).
YTDLP_PLAYER_CLIENT = "default,-web"
YTDLP_PLAYER_CLIENTS = ("default,-web", "android_vr", "ios")


def _fetch_transcript_ytdlp_once(
    video_id: str,
    sub_langs: str,
    player_client: str,
    cookie_args: list[str],
) -> str:
    import tempfile

    url = f"https://www.youtube.com/watch?v={video_id}"
    with tempfile.TemporaryDirectory(prefix="yt-subs-") as tmp:
        out = str(Path(tmp) / "sub")
        cmd = [sys.executable, "-m", "yt_dlp", *cookie_args]
        cmd.extend(
            [
                "--skip-download",
                "--ignore-no-formats-error",
                "--sleep-subtitles",
                "2",
                "--extractor-args",
                f"youtube:player_client={player_client}",
                "--write-auto-sub",
                "--write-sub",
                "--sub-langs",
                sub_langs,
                "--convert-subs",
                "vtt",
                "--no-playlist",
                "-o",
                out,
                url,
            ]
        )
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, env=ytdlp_subprocess_env()
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()
            raise RuntimeError(f"yt-dlp subtitle fetch failed: {err[:500]}")
        vtt_files = sorted(Path(tmp).glob("*.vtt"), key=lambda p: p.stat().st_size, reverse=True)
        if not vtt_files:
            raise RuntimeError("yt-dlp did not produce any subtitle file")
        plain = _parse_vtt_to_plain(vtt_files[0].read_text(encoding="utf-8", errors="replace"))
        if len(plain) < 50:
            raise RuntimeError("yt-dlp subtitle file was too short or empty")
        return plain


def fetch_transcript_ytdlp(video_id: str, languages: list[str] | None = None) -> tuple[list, str]:
    """Fallback when youtube-transcript-api is IP-blocked."""
    langs = languages or ["hi", "en"]
    cookie_args = ytdlp_cookie_cli_args()
    # Try English first — Hindi subtitle endpoint often 429s before en on rate-limited IPs.
    sub_lang_batches = [
        ",".join(dict.fromkeys([*langs, "en", "en-US", "en-GB", "en-orig"])),
        "en,en-US,en-GB,en-orig",
    ]
    last_err: Exception | None = None
    for player_client in YTDLP_PLAYER_CLIENTS:
        for sub_langs in sub_lang_batches:
            try:
                plain = _fetch_transcript_ytdlp_once(
                    video_id, sub_langs, player_client, cookie_args
                )
                return [], plain
            except Exception as exc:
                last_err = exc
    raise RuntimeError(str(last_err or "yt-dlp subtitle fetch failed"))


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> tuple[list, str]:
    langs = languages or ["hi", "en"]
    api_exc: Exception | None = None
    try:
        api = YouTubeTranscriptApi()
        result = api.fetch(video_id, languages=langs)
        plain = " ".join(segment.text for segment in result)
        print(f"[transcript] api for {video_id}", file=sys.stderr)
        return result, plain
    except Exception as exc:
        api_exc = exc
    if youtube_has_auth_cookies():
        try:
            result, plain = fetch_transcript_ytdlp(video_id, langs)
            tag = youtube_cookies_browser() or "cookies-file"
            print(f"[transcript] yt-dlp+{tag} for {video_id}", file=sys.stderr)
            return result, plain
        except Exception as cookies_exc:
            print(
                f"[transcript] yt-dlp+cookies failed for {video_id}: {cookies_exc}",
                file=sys.stderr,
            )
    try:
        result, plain = fetch_transcript_ytdlp(video_id, langs)
        print(f"[transcript] youtube-transcript-api blocked — used yt-dlp for {video_id}", file=sys.stderr)
        return result, plain
    except Exception as ytdlp_exc:
        raise RuntimeError(
            f"Transcript fetch failed for {video_id}. "
            f"API error: {api_exc}. yt-dlp fallback: {ytdlp_exc}"
        ) from ytdlp_exc


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
