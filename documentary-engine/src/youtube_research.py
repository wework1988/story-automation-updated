"""Context-aware, channel-first YouTube research → transcripts → combined research.

Flow: download the seed transcript first, work out what the video is really
about, then search priority channels (and YouTube at large) with queries built
from that context. Candidates are accepted only if their own transcript
discusses the same subject.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus

from youtube_transcript_api import YouTubeTranscriptApi

from .channels import DEFAULT_PRIORITY_CHANNELS
from .context import (
    SeedContext,
    build_seed_context,
    source_dominance,
    title_relevance,
    title_search_query,
    transcript_relevance,
)


REACTION_PATTERNS = re.compile(
    r"\b(reaction|reacts to|clip|shorts|#shorts|compilation|highlights only|"
    r"funny moments|meme|trailer reaction)\b",
    re.IGNORECASE,
)


def log(msg: str) -> None:
    print(f"[research] {msg}", flush=True)


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
    title = re.sub(r'[<>:"/\\|?*]', "", title)
    return re.sub(r"\s+", " ", title).strip()


def channel_handle(url: str) -> str:
    match = re.search(r"youtube\.com/(@[\w.-]+)", url)
    return match.group(1) if match else url.rstrip("/").split("/")[-1]


def search_query_from_title(title: str) -> str:
    return title_search_query(title)


def fetch_metadata(video_id: str) -> dict:
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--dump-json",
        "--no-download",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    try:
        data = json.loads(subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=90))
    except Exception as exc:
        log(f"metadata fetch failed for {video_id}: {exc}")
        return {"video_id": video_id, "title": video_id, "view_count": 0}

    return {
        "video_id": data.get("id", video_id),
        "title": data.get("title", video_id),
        "channel": data.get("channel"),
        "channel_id": data.get("channel_id"),
        "channel_url": data.get("channel_url"),
        "youtube_url": data.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}",
        "upload_date": data.get("upload_date") or "",
        "duration_seconds": data.get("duration") or 0,
        "view_count": data.get("view_count") or 0,
        "description": (data.get("description") or "")[:2000],
        "tags": data.get("tags") or [],
    }


def search_channel(channel_url: str, query: str, limit: int = 10) -> list[tuple[str, str]]:
    handle = channel_handle(channel_url)
    search_url = f"https://www.youtube.com/{handle}/search?query={quote_plus(query)}"
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--flat-playlist",
        f"--playlist-end={limit}",
        "--print",
        "%(id)s|%(title)s",
        search_url,
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=120)
    except subprocess.CalledProcessError:
        return []
    except subprocess.TimeoutExpired:
        log(f"  search timed out on {handle} for {query!r}")
        return []

    results: list[tuple[str, str]] = []
    for line in out.splitlines():
        if "|" not in line:
            continue
        vid, title = line.split("|", 1)
        vid, title = vid.strip(), title.strip()
        if vid and title:
            results.append((vid, title))
    return results


def search_youtube_global(query: str, limit: int) -> list[tuple[str, str]]:
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--flat-playlist",
        f"--playlist-end={limit}",
        "--print",
        "%(id)s|%(title)s",
        f"ytsearch{limit}:{query}",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=180)
    except subprocess.CalledProcessError:
        return []
    except subprocess.TimeoutExpired:
        log(f"  global search timed out for {query!r}")
        return []

    results: list[tuple[str, str]] = []
    for line in out.splitlines():
        if "|" not in line:
            continue
        vid, title = line.split("|", 1)
        results.append((vid.strip(), title.strip()))
    return results


def is_disqualified(meta: dict, *, min_views: int, min_duration_seconds: int) -> str | None:
    title = meta.get("title") or ""
    views = meta.get("view_count") or 0
    duration = meta.get("duration_seconds") or 0

    if views < min_views:
        return f"views below minimum ({views:,} < {min_views:,})"
    if duration and duration < min_duration_seconds:
        return f"too short ({duration}s)"
    if REACTION_PATTERNS.search(title):
        return "reaction/clip pattern in title"
    return None


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> tuple[list[dict], str]:
    if languages is None:
        languages = ["hi", "en", "hi-IN", "en-IN"]

    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id, languages=languages)
    except Exception:
        fetched = api.fetch(video_id)

    segments = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
    plain = " ".join(s["text"] for s in segments).replace("\n", " ")
    plain = re.sub(r"\s+", " ", plain).strip()
    return segments, plain


@dataclass
class Candidate:
    meta: dict
    title_score: float
    source: str  # priority_channel | fallback | seed
    channel_handle: str | None
    matched_query: str


@dataclass
class SelectedVideo:
    meta: dict
    transcript: str
    source: str
    channel_handle: str | None
    relevance: float
    content_relevance: float


def rank_key(candidate: Candidate) -> tuple:
    """Group by relevance band, then prefer the highest-view video in that band."""
    band = round(candidate.title_score * 4) / 4
    return (band, candidate.meta.get("view_count") or 0)


def find_videos_on_channels(
    *,
    ctx: SeedContext,
    channels: list[str],
    seed_id: str | None,
    per_channel_limit: int,
    min_relevance: float,
) -> list[Candidate]:
    best: dict[str, Candidate] = {}

    for channel_url in channels:
        handle = channel_handle(channel_url)
        for query in ctx.queries:
            log(f"Searching {handle} for {query!r}")
            for vid, flat_title in search_channel(channel_url, query, per_channel_limit):
                if vid == seed_id:
                    continue
                score = title_relevance(flat_title, ctx)
                if score < min_relevance:
                    continue
                existing = best.get(vid)
                if existing and existing.title_score >= score:
                    continue
                meta = existing.meta if existing else fetch_metadata(vid)
                meta_title = meta.get("title") or flat_title
                score = max(score, title_relevance(meta_title, ctx))
                if score < min_relevance:
                    continue
                best[vid] = Candidate(
                    meta=meta,
                    title_score=score,
                    source="priority_channel",
                    channel_handle=handle,
                    matched_query=query,
                )
                if not existing:
                    log(f"  match {score:.2f} — {meta_title[:70]} ({(meta.get('view_count') or 0):,} views)")

    ranked = sorted(best.values(), key=rank_key, reverse=True)
    return ranked


def find_fallback_videos(
    *,
    ctx: SeedContext,
    seed_id: str | None,
    search_limit: int,
    min_relevance: float,
    exclude_ids: set[str],
) -> list[Candidate]:
    best: dict[str, Candidate] = {}

    for query in ctx.queries:
        log(f"Searching YouTube for {query!r}")
        for vid, flat_title in search_youtube_global(query, search_limit):
            if vid in exclude_ids or vid == seed_id:
                continue
            score = title_relevance(flat_title, ctx)
            if score < min_relevance:
                continue
            existing = best.get(vid)
            if existing and existing.title_score >= score:
                continue
            meta = existing.meta if existing else fetch_metadata(vid)
            meta_title = meta.get("title") or flat_title
            score = max(score, title_relevance(meta_title, ctx))
            if score < min_relevance:
                continue
            best[vid] = Candidate(
                meta=meta,
                title_score=score,
                source="fallback",
                channel_handle=None,
                matched_query=query,
            )
            if not existing:
                log(f"  fallback {score:.2f} — {meta_title[:70]} ({(meta.get('view_count') or 0):,} views)")

    return sorted(best.values(), key=rank_key, reverse=True)


def collect_transcripts(
    candidates: list[Candidate],
    *,
    ctx: SeedContext,
    languages: list[str],
    target_count: int,
    min_views: int,
    min_duration_seconds: int,
    min_content_relevance: float,
    rejected: list[dict],
) -> list[SelectedVideo]:
    selected: list[SelectedVideo] = []

    for candidate in candidates:
        if len(selected) >= target_count:
            break
        meta = candidate.meta
        title = meta.get("title") or meta.get("video_id", "")
        reason = is_disqualified(meta, min_views=min_views, min_duration_seconds=min_duration_seconds)
        if reason:
            log(f"  skip {title[:60]} — {reason}")
            rejected.append({"title": title, "reason": reason})
            continue

        try:
            _, plain = fetch_transcript(meta["video_id"], languages)
        except Exception as exc:
            log(f"  transcript FAILED {meta['video_id']}: {exc}")
            rejected.append({"title": title, "reason": f"transcript unavailable: {exc}"})
            continue

        content_score = transcript_relevance(plain, ctx)
        if content_score < min_content_relevance:
            log(f"  drop {title[:60]} — off-topic content ({content_score:.2f} < {min_content_relevance:.2f})")
            rejected.append({"title": title, "reason": f"content relevance {content_score:.2f} below threshold"})
            continue

        log(f"  keep {title[:60]} — content relevance {content_score:.2f}")
        selected.append(
            SelectedVideo(
                meta=meta,
                transcript=plain,
                source=candidate.source,
                channel_handle=candidate.channel_handle,
                relevance=candidate.title_score,
                content_relevance=content_score,
            )
        )

    return selected


def run_channel_first_research(
    url: str,
    *,
    output_dir: Path,
    channels: list[str] | None = None,
    target_count: int = 4,
    min_channel_count: int = 3,
    per_channel_limit: int = 10,
    search_limit: int = 20,
    min_views: int = 10_000,
    min_duration_seconds: int = 180,
    min_relevance: float = 0.35,
    min_content_relevance: float = 0.50,
    max_queries: int = 3,
    languages: list[str] | None = None,
) -> Path:
    """Seed transcript → topic context → channel-first search → combined research."""
    if channels is None:
        channels = DEFAULT_PRIORITY_CHANNELS
    if languages is None:
        languages = ["hi", "en"]

    seed_id = extract_video_id(url)
    seed_meta = fetch_metadata(seed_id)

    output_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir = output_dir / "transcripts"
    transcripts_dir.mkdir(exist_ok=True)

    log(f"Seed: {seed_meta.get('title')}")

    seed_transcript = ""
    try:
        _, seed_transcript = fetch_transcript(seed_id, languages)
        log(f"Seed transcript: {len(seed_transcript):,} chars — building topic context from content")
    except Exception as exc:
        log(f"Seed transcript unavailable ({exc}) — falling back to title-only context")

    ctx = build_seed_context(
        seed_meta.get("title") or seed_id,
        seed_transcript,
        tags=seed_meta.get("tags") or [],
        channel=seed_meta.get("channel") or "",
        max_queries=max_queries,
    )
    log(f"Topic subjects: {', '.join(ctx.subjects[:8]) or 'none detected'}")
    log(f"Corroborated tags: {ctx.tags[:5] or 'none'}")
    log(f"Search queries: {ctx.queries}")
    log(f"Output: {output_dir}")

    rejected: list[dict] = []
    channel_candidates = find_videos_on_channels(
        ctx=ctx,
        channels=channels,
        seed_id=seed_id,
        per_channel_limit=per_channel_limit,
        min_relevance=min_relevance,
    )

    seed_selected: list[SelectedVideo] = []
    if seed_transcript:
        seed_selected = [
            SelectedVideo(
                meta=seed_meta,
                transcript=seed_transcript,
                source="seed",
                channel_handle=None,
                relevance=1.0,
                content_relevance=1.0,
            )
        ]

    remaining = max(0, target_count - len(seed_selected))
    selected = list(seed_selected)

    selected += collect_transcripts(
        channel_candidates,
        ctx=ctx,
        languages=languages,
        target_count=remaining,
        min_views=min_views,
        min_duration_seconds=min_duration_seconds,
        min_content_relevance=min_content_relevance,
        rejected=rejected,
    )

    channel_count = sum(1 for v in selected if v.source == "priority_channel")
    if channel_count < min_channel_count and len(selected) < target_count:
        log(
            f"Only {channel_count} usable priority-channel sources (want {min_channel_count}) "
            "— filling from general YouTube search"
        )
        exclude = {v.meta["video_id"] for v in selected} | {c.meta["video_id"] for c in channel_candidates}
        fallback_candidates = find_fallback_videos(
            ctx=ctx,
            seed_id=seed_id,
            search_limit=search_limit,
            min_relevance=min_relevance,
            exclude_ids=exclude,
        )
        selected += collect_transcripts(
            fallback_candidates,
            ctx=ctx,
            languages=languages,
            target_count=target_count - len(selected),
            min_views=min_views,
            min_duration_seconds=min_duration_seconds,
            min_content_relevance=min_content_relevance,
            rejected=rejected,
        )

    if not selected:
        raise RuntimeError("No usable transcripts found after context-aware channel-first search")

    def sort_key(v: SelectedVideo) -> tuple:
        is_seed = 0 if v.meta.get("video_id") == seed_id else 1
        upload = v.meta.get("upload_date") or "99999999"
        return (is_seed, upload)

    selected.sort(key=sort_key)

    entries = []
    blocks: list[str] = []
    for idx, v in enumerate(selected, 1):
        filename = f"{slug_title(v.meta.get('title') or v.meta['video_id'])}.txt"
        (transcripts_dir / filename).write_text(v.transcript, encoding="utf-8")
        entry = {
            "rank": idx,
            "video_id": v.meta["video_id"],
            "youtube_url": v.meta.get("youtube_url"),
            "title": v.meta.get("title"),
            "channel": v.meta.get("channel"),
            "channel_handle": v.channel_handle,
            "view_count": v.meta.get("view_count"),
            "upload_date": v.meta.get("upload_date"),
            "duration_seconds": v.meta.get("duration_seconds"),
            "source": v.source,
            "relevance": round(v.relevance, 3),
            "content_relevance": round(v.content_relevance, 3),
            "filename": filename,
            "transcript_characters": len(v.transcript),
        }
        entries.append(entry)
        header = (
            f"=== SOURCE {idx}: {entry['title']} ===\n"
            f"Channel: {entry.get('channel') or 'unknown'}\n"
            f"URL: {entry.get('youtube_url')}\n"
            f"Upload: {entry.get('upload_date') or 'unknown'} | "
            f"Views: {(entry.get('view_count') or 0):,} | "
            f"Topic match: {entry['content_relevance']}\n"
        )
        blocks.append(f"{header}\n{v.transcript}")

    (output_dir / "videos.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    dominance = source_dominance([(f"SOURCE {e['rank']}", v.transcript) for e, v in zip(entries, selected)])

    priority_count = sum(1 for e in entries if e["source"] == "priority_channel")
    meta_doc = {
        "seed_video_id": seed_id,
        "seed_youtube_url": url,
        "seed_title": seed_meta.get("title"),
        "seed_transcript_characters": len(seed_transcript),
        "context_from_transcript": ctx.from_transcript,
        "topic_subjects": ctx.subjects,
        "story_primary": ctx.primary,
        "story_angle": ctx.angle,
        "corroborated_tags": ctx.tags,
        "topic_entities": ctx.entities[:12],
        "topic_keywords": ctx.keywords[:20],
        "search_queries": ctx.queries,
        "priority_channels": [channel_handle(c) for c in channels],
        "selected_count": len(entries),
        "priority_channel_count": priority_count,
        "used_channel_only": priority_count >= min_channel_count,
        "rejected": rejected[:20],
        "source_dominance": dominance,
        "ordering": "seed_first_then_upload_date_asc",
    }
    (output_dir / "research-meta.json").write_text(
        json.dumps(meta_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    combined = build_combined_research(
        entries=entries,
        blocks=blocks,
        ctx=ctx,
        dominance=dominance,
        priority_count=priority_count,
    )
    (output_dir / "COMBINED_RESEARCH.txt").write_text(combined, encoding="utf-8")

    total_chars = sum(e["transcript_characters"] for e in entries)
    log(f"Done: {len(entries)} transcripts ({total_chars:,} chars) → {output_dir / 'COMBINED_RESEARCH.txt'}")
    if dominance.get("warning"):
        log(f"Dominance warning: {dominance['warning']}")
    return output_dir


def build_combined_research(
    *,
    entries: list[dict],
    blocks: list[str],
    ctx: SeedContext,
    dominance: dict,
    priority_count: int,
) -> str:
    lines = [
        "RESEARCH MATERIAL — facts and events only.",
        "Use as reference for your own original narration. Do not copy phrasing,",
        "and do not reuse any single source's order or selection of details.",
        "",
        f"Topic: {ctx.title_query}",
    ]
    if ctx.subjects:
        lines.append(f"Key subjects: {', '.join(ctx.subjects[:8])}")
    lines.append(f"Sources: {len(entries)} videos ({priority_count} from priority channels)")

    lines.append("")
    lines.append("SOURCE DOMINANCE MAP (share of unique numbers and names):")
    for item in dominance.get("sources", []):
        lines.append(f"  {item['source']}: {item['share'] * 100:.0f}% ({item['unique_details']} unique details)")

    if dominance.get("warning"):
        lines += [
            "",
            "⚠ SINGLE-SOURCE DOMINANCE DETECTED",
            f"  {dominance['warning']}",
            "  Mandatory for every beat built on that source:",
            "    1. Reorder its details — never present them in the source's order.",
            "    2. Cut at least a third of its niche details; keep only what the causal chain needs.",
            "    3. Interleave the remaining details with the human-anchor thread or a confirmed fact",
            "       from another source, so the beat is never a straight run of one source's material.",
            "    4. Drop that source's dramatised framings entirely; build your own from the bare facts.",
        ]

    lines += ["", "=" * 60, "", ""]
    return "\n".join(lines) + "\n\n---\n\n".join(blocks)
