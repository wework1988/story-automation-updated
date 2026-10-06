"""Local cms-generate-stories folder sync (mirror of Drupal Story node)."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CMS_ROOT = REPO_ROOT / "cms-generate-stories"


@dataclass
class LocalCmsStory:
    cms_dir: Path
    node_id: str
    title: str
    story_type: str
    youtube_urls: list[str]
    duration_minutes: int


def _read_meta_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


def find_cms_dir_by_node_id(node_id: str | int, *, cms_root: Path = CMS_ROOT) -> Path | None:
    needle = str(node_id).strip()
    for meta_file in cms_root.rglob("meta/drupal-node-id.txt"):
        if _read_meta_file(meta_file) == needle:
            return meta_file.parent.parent
    return None


def load_local_story(cms_dir: Path) -> LocalCmsStory:
    meta = cms_dir / "meta"
    urls_file = meta / "youtube-urls.txt"
    urls: list[str] = []
    if urls_file.is_file():
        for line in urls_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    duration_raw = _read_meta_file(meta / "duration-minutes.txt")
    duration = int(duration_raw) if duration_raw.isdigit() else 12
    return LocalCmsStory(
        cms_dir=cms_dir,
        node_id=_read_meta_file(meta / "drupal-node-id.txt"),
        title=_read_meta_file(meta / "story-title.txt"),
        story_type=_read_meta_file(meta / "story-type.txt") or "general",
        youtube_urls=urls,
        duration_minutes=duration,
    )


def sync_outputs_to_cms(
    cms_dir: Path,
    *,
    research_dir: Path,
    story_dir: Path,
    story_meta: str,
) -> None:
    """Copy pipeline outputs into cms-generate-stories/{node}/script/."""
    script = cms_dir / "script"
    prompts = cms_dir / "prompts"
    script.mkdir(parents=True, exist_ok=True)
    prompts.mkdir(parents=True, exist_ok=True)

    mapping = [
        (story_dir / "FULL_STORY.txt", script / "FULL_STORY.txt"),
        (story_dir / "prompt.txt", prompts / "prompt.txt"),
        (story_dir / "raw.md", script / "raw.md"),
        (story_dir / "meta.json", script / "pipeline-meta.json"),
        (research_dir / "story_pointers.txt", script / "story_pointers.txt"),
    ]
    for src, dest in mapping:
        if src.is_file():
            shutil.copy2(src, dest)

    (script / "story_meta.txt").write_text(story_meta.strip() + "\n", encoding="utf-8")

    pointers_raw = research_dir / "bullet_extract_raw"
    if pointers_raw.is_dir():
        dest_raw = script / "bullet_extract_raw"
        if dest_raw.exists():
            shutil.rmtree(dest_raw)
        shutil.copytree(pointers_raw, dest_raw)


def build_story_meta(result_chars: int, target_chars: int, *, pipeline: str) -> str:
    low = target_chars - 500
    high = target_chars + 500
    status = "PASS" if low <= result_chars <= high else "OUT OF RANGE"
    return (
        "POST-WRITE CHARACTER COUNT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Actual character count: {result_chars:,}\n"
        f"Target range: {low:,} – {high:,}\n"
        f"Status: {status}\n"
        f"Pipeline: {pipeline}\n"
    )
