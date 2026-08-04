"""YouTube research: seed URL → related videos → download transcripts."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from library.fetch_youtube_transcript import (
    extract_video_id,
    fetch_transcript,
    fetch_yt_metadata,
    slug_title,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESEARCH_DIR = REPO_ROOT / "research-storage-stories"
OUTPUTFINAL_DIRNAME = "outputfinal"


def folder_slug_from_title(title: str) -> str:
    title = re.sub(r"\s*\|\s*2D Animation\s*$", "", title, flags=re.I).strip()
    base = title.split(":")[0].strip() or title
    base = re.sub(r"[#@]", "", base)
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    if not slug:
        slug = "story"
    if not slug.endswith("-research"):
        slug = f"{slug}-research"
    return slug[:80]


def research_folder_slug(research_dir: Path) -> str:
    name = research_dir.name
    return name.removesuffix("-research") if name.endswith("-research") else name


def story_output_dir(research_dir: Path) -> Path:
    """Generated story lives next to transcripts: .../{case}-research/outputfinal/"""
    return research_dir / OUTPUTFINAL_DIRNAME


def search_query_from_title(title: str) -> str:
    title = re.sub(r"\s*\|\s*2D Animation\s*$", "", title, flags=re.I)
    title = re.sub(r"M#rder", "murder", title, flags=re.I)
    title = re.sub(r"[#@]", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    if ":" in title:
        head, _ = title.split(":", 1)
        if len(head.split()) >= 3:
            return head.strip()
    return title[:120]


def search_youtube(query: str, limit: int) -> list[tuple[str, str, int]]:
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--flat-playlist",
        f"--playlist-end={limit}",
        "--print",
        "%(id)s|%(title)s|%(view_count)s",
        f"ytsearch{limit}:{query}",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=120)
    except subprocess.CalledProcessError:
        return []

    results: list[tuple[str, str, int]] = []
    for line in out.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        vid, title = parts[0], parts[1]
        views = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else 0
        results.append((vid, title, views))
    return results


def find_related_videos(
    seed_id: str,
    seed_title: str,
    *,
    related_count: int,
    search_limit: int,
    min_views: int,
) -> list[tuple[str, str, int]]:
    query = search_query_from_title(seed_title)
    print(f"[research] Searching YouTube: {query!r}")

    ranked: list[tuple[str, str, int]] = []
    for vid, title, flat_views in search_youtube(query, search_limit):
        if vid == seed_id:
            continue
        meta = fetch_yt_metadata(vid)
        views = meta.get("view_count") or flat_views or 0
        if views < min_views:
            continue
        ranked.append((vid, meta.get("title") or title, views))

    ranked.sort(key=lambda item: item[2], reverse=True)
    return ranked[:related_count]


def load_videos_json(path: Path) -> list[dict]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def save_videos_json(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries.sort(key=lambda e: e.get("view_count") or 0, reverse=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def upsert_entry(entries: list[dict], entry: dict) -> list[dict]:
    entries = [e for e in entries if e.get("video_id") != entry.get("video_id")]
    entries.append(entry)
    return entries


def download_video_transcript(
    video_id: str,
    output_dir: Path,
    *,
    role: str,
    languages: list[str],
    force: bool = False,
    entries: list[dict] | None = None,
) -> dict | None:
    if entries and not force:
        for existing in entries:
            if existing.get("video_id") != video_id:
                continue
            filename = existing.get("filename")
            if not filename:
                break
            path = output_dir / filename
            if path.exists() and path.stat().st_size > 100:
                print(
                    f"[research] reusing existing {filename} "
                    f"({path.stat().st_size:,} bytes, skip download)"
                )
                return existing

    yt_meta = fetch_yt_metadata(video_id)
    try:
        result, plain = fetch_transcript(video_id, languages)
    except Exception as exc:
        print(f"[research] transcript FAILED ({video_id}): {exc}", file=sys.stderr)
        if entries:
            for existing in entries:
                if existing.get("video_id") != video_id:
                    continue
                filename = existing.get("filename")
                if not filename:
                    break
                path = output_dir / filename
                if path.exists() and path.stat().st_size > 100:
                    print(
                        f"[research] using existing file after fetch failure: {filename}",
                        file=sys.stderr,
                    )
                    return existing
        return None

    title = yt_meta.get("title") or video_id
    filename = f"{slug_title(title)}.txt"
    (output_dir / filename).write_text(plain, encoding="utf-8")

    entry = {
        "video_id": video_id,
        "youtube_url": yt_meta.get("youtube_url") or f"https://www.youtube.com/watch?v={video_id}",
        "title": title,
        "filename": filename,
        "transcript_characters": len(plain),
        "transcript_words": len(plain.split()),
        "transcript_segments": len(result),
        "channel": yt_meta.get("channel"),
        "view_count": yt_meta.get("view_count") or 0,
        "role": role,
    }
    print(
        f"[research] saved {filename} ({len(plain):,} chars, {entry['view_count']:,} views)"
    )
    return entry


def resolve_output_dir(base: Path, folder_name: str | None, seed_title: str, seed_id: str) -> Path:
    slug = folder_name or folder_slug_from_title(seed_title)
    out = base / slug
    if out.exists() and not folder_name:
        existing = load_videos_json(out / "videos.json")
        if existing and not any(e.get("video_id") == seed_id for e in existing):
            out = base / f"{slug}-{seed_id[:6]}"
    return out


def run_research(
    url: str,
    *,
    output_base: Path = DEFAULT_RESEARCH_DIR,
    folder_name: str | None = None,
    languages: list[str] | None = None,
    force: bool = False,
    explicit_related_urls: list[str],
) -> Path:
    """Download seed + user-provided source URLs. No automatic YouTube search."""
    if not explicit_related_urls:
        raise ValueError(
            "explicit_related_urls required — provide 2+ YouTube URLs via queue, "
            "--urls-file, or --video-urls"
        )
    if languages is None:
        languages = ["hi", "en"]

    seed_id = extract_video_id(url)
    seed_meta = fetch_yt_metadata(seed_id)
    seed_title = seed_meta.get("title") or seed_id

    output_dir = resolve_output_dir(output_base, folder_name, seed_title, seed_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    videos_json = output_dir / "videos.json"
    entries = load_videos_json(videos_json)

    print(f"[research] Seed: {seed_title}")
    print(f"[research] Output: {output_dir}")

    if force or not any(e.get("video_id") == seed_id for e in entries):
        print(f"[research] Downloading seed ({seed_id})")
        entry = download_video_transcript(
            seed_id, output_dir, role="seed", languages=languages, force=force, entries=entries
        )
        if entry:
            entries = upsert_entry(entries, entry)
            save_videos_json(videos_json, entries)
        elif any(e.get("video_id") == seed_id for e in entries):
            print("[research] Seed download failed — continuing with existing seed transcript on disk")
    else:
        print("[research] Seed already downloaded (use --force to redo)")

    existing_ids = {e.get("video_id") for e in entries}
    want_ids = [extract_video_id(u) for u in explicit_related_urls if u.strip()]
    want_ids = [vid for vid in want_ids if vid and vid != seed_id]
    print(f"[research] Downloading {len(want_ids)} provided source URL(s)")
    for vid in want_ids:
        if vid in existing_ids and not force:
            print(f"[research] source already present: {vid}")
            continue
        entry = download_video_transcript(
            vid, output_dir, role="related", languages=languages, force=force, entries=entries
        )
        if entry:
            entries = upsert_entry(entries, entry)
            save_videos_json(videos_json, entries)
            existing_ids.add(vid)

    source_count = len([e for e in entries if e.get("video_id")])

    (output_dir / "research-meta.json").write_text(
        json.dumps(
            {
                "seed_video_id": seed_id,
                "seed_youtube_url": url,
                "seed_title": seed_title,
                "source_urls": [url, *explicit_related_urls],
                "source_count": source_count,
                "output_dir": str(output_dir),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"[research] Done: {source_count} videos in {output_dir}")
    return output_dir


def combine_transcripts(
    research_dir: Path, *, max_related: int | None = None
) -> tuple[str, int, list[dict]]:
    videos_json = research_dir / "videos.json"
    if not videos_json.exists():
        raise FileNotFoundError(f"No videos.json in {research_dir}")

    videos = json.loads(videos_json.read_text(encoding="utf-8"))
    if not videos:
        raise RuntimeError(f"No videos in {videos_json}")

    blocks: list[str] = []
    total_chars = 0
    used: list[dict] = []
    related_used = 0

    for entry in sorted(
        videos, key=lambda v: (v.get("role") != "seed", -(v.get("view_count") or 0))
    ):
        role = entry.get("role") or "video"
        if role != "seed":
            if max_related is not None and max_related >= 0 and related_used >= max_related:
                continue
            related_used += 1
        filename = entry.get("filename")
        if not filename:
            continue
        path = research_dir / filename
        if not path.exists():
            print(f"[research] skip missing transcript: {filename}")
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        title = entry.get("title") or filename
        header = f"=== {title} ({role}) ===\n{entry.get('youtube_url', '')}"
        blocks.append(f"{header}\n\n{text}")
        total_chars += len(text)
        used.append(entry)

    if not blocks:
        raise RuntimeError(f"No transcript text found in {research_dir}")

    return "\n\n---\n\n".join(blocks), total_chars, used
