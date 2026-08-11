"""Importable channel-first YouTube research for CMS worker."""

from __future__ import annotations

import json
from pathlib import Path

from .youtube_research import run_channel_first_research


def run_research(
    seed_url: str,
    output_dir: Path,
    *,
    target_count: int = 4,
    min_channel_count: int = 3,
    min_views: int = 10_000,
) -> tuple[Path, str, dict]:
    """Run channel-first research; return output_dir, combined text, meta dict."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    run_channel_first_research(
        seed_url,
        output_dir=output_dir,
        target_count=target_count,
        min_channel_count=min_channel_count,
        min_views=min_views,
    )

    combined_path = output_dir / "COMBINED_RESEARCH.txt"
    if not combined_path.is_file():
        raise RuntimeError(f"Research failed: missing {combined_path}")

    combined_text = combined_path.read_text(encoding="utf-8").strip()
    if not combined_text:
        raise RuntimeError("Research failed: COMBINED_RESEARCH.txt is empty")

    meta: dict = {}
    meta_path = output_dir / "research-meta.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

    return output_dir, combined_text, meta
