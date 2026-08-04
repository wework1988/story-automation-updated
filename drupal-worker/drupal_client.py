"""Drupal Story Pipeline API client (Pipeline 1 — generate story from YouTube)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class DrupalStory:
    id: str
    title: str
    story_type: str
    youtube_urls: list[str]
    duration_minutes: int
    status: str
    full_story: str
    story_meta: str
    characters_info: str


def _base_url() -> str:
    base = os.environ.get("DRUPAL_BASE_URL", "").strip().rstrip("/")
    if not base:
        raise RuntimeError("DRUPAL_BASE_URL not set in environment")
    return base


def _api_key() -> str:
    key = os.environ.get("DRUPAL_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DRUPAL_API_KEY not set in environment")
    return key


def _request(method: str, path: str, body: dict | None = None) -> dict[str, Any]:
    url = f"{_base_url()}{path}"
    data = None
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"Drupal API {method} {path} failed ({exc.code}): {detail}") from exc


def fetch_story(story_id: str) -> DrupalStory:
    data = _request("GET", f"/api/story-pipeline/stories/{story_id}")
    urls = data.get("youtube_urls") or data.get("field_youtube_urls") or []
    if isinstance(urls, str):
        urls = [u.strip() for u in urls.splitlines() if u.strip()]
    duration = int(data.get("duration_minutes") or data.get("field_duration_minutes") or 12)
    return DrupalStory(
        id=str(data.get("id") or story_id),
        title=str(data.get("title") or ""),
        story_type=str(data.get("story_type") or "general").lower(),
        youtube_urls=list(urls),
        duration_minutes=duration,
        status=str(data.get("status") or "draft"),
        full_story=str(data.get("full_story") or data.get("field_full_story") or ""),
        story_meta=str(data.get("story_meta") or data.get("field_story_meta") or ""),
        characters_info=str(data.get("characters_info") or data.get("field_characters_info") or ""),
    )


def push_story_outputs(
    story_id: str,
    *,
    full_story: str,
    story_meta: str,
    status: str = "story_generated",
) -> dict[str, Any]:
    return _request(
        "PATCH",
        f"/api/story-pipeline/stories/{story_id}",
        {
            "full_story": full_story,
            "story_meta": story_meta,
            "status": status,
        },
    )


def enqueue_generate_story(story_id: str) -> dict[str, Any]:
    """Optional: CMS button hits this; worker polls or runs --story-id directly."""
    return _request("POST", "/api/story-pipeline/generate-story", {"story_id": story_id})
