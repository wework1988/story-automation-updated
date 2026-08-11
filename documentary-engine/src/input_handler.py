"""Phase 1 — accept topic, YouTube URL, PDF, article, or notes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen

from .schemas import slugify
from .youtube_research import extract_video_id, fetch_metadata


def log(msg: str) -> None:
    print(f"[input] {msg}", flush=True)


@dataclass
class DocumentaryInput:
    input_type: str
    raw_value: str
    topic: str
    youtube_url: str | None
    duration_minutes: int
    folder_name: str | None
    series_id: str | None
    supplemental_text: str


def _read_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8", errors="replace").strip()


def _fetch_url_text(url: str, max_chars: int = 50_000) -> str:
    req = Request(url, headers={"User-Agent": "DocumentaryEngine/1.0"})
    with urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return raw[:max_chars]


def _topic_from_pdf(path: Path) -> tuple[str, str]:
    topic = path.stem.replace("-", " ").replace("_", " ")
    note = (
        f"[PDF source path: {path}]\n"
        "PDF text was not extracted locally. The gap-research agent will use "
        "DeepSeek web search to verify facts from this document's subject matter."
    )
    return topic, note


def parse_queue_line(line: str, line_no: int) -> DocumentaryInput | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    parts = [p.strip() for p in stripped.split(",")]
    if len(parts) < 3:
        raise ValueError(
            f"Line {line_no}: expected input_type,input_value,duration_minutes[,folder][,series_id]"
        )

    input_type = parts[0].lower()
    raw_value = parts[1]
    duration = int(parts[2])
    folder_name = parts[3] if len(parts) > 3 else None
    series_id = parts[4] if len(parts) > 4 else None

    return build_input(
        input_type=input_type,
        raw_value=raw_value,
        duration_minutes=duration,
        folder_name=folder_name,
        series_id=series_id,
    )


def build_input(
    *,
    input_type: str,
    raw_value: str,
    duration_minutes: int,
    folder_name: str | None = None,
    series_id: str | None = None,
) -> DocumentaryInput:
    input_type = input_type.lower()
    supplemental = ""
    youtube_url: str | None = None
    topic = raw_value.strip()

    if input_type == "youtube":
        youtube_url = raw_value.strip()
        vid = extract_video_id(youtube_url)
        meta = fetch_metadata(vid)
        topic = meta.get("title") or vid
    elif input_type == "topic":
        topic = raw_value.strip()
    elif input_type == "pdf":
        path = Path(raw_value).expanduser().resolve()
        topic, supplemental = _topic_from_pdf(path)
    elif input_type == "article":
        supplemental = _fetch_url_text(raw_value.strip())
        topic = raw_value.strip().split("/")[-1].replace("-", " ")[:80] or "article-topic"
    elif input_type == "notes":
        path = Path(raw_value).expanduser().resolve()
        supplemental = _read_text_file(path)
        topic = path.stem.replace("-", " ").replace("_", " ")
    else:
        raise ValueError(f"Unknown input_type: {input_type!r}. Use youtube|topic|pdf|article|notes")

    if not folder_name:
        folder_name = slugify(topic)

    log(f"type={input_type} topic={topic!r} duration={duration_minutes}min folder={folder_name}")

    return DocumentaryInput(
        input_type=input_type,
        raw_value=raw_value,
        topic=topic,
        youtube_url=youtube_url,
        duration_minutes=duration_minutes,
        folder_name=folder_name,
        series_id=series_id,
        supplemental_text=supplemental,
    )


def save_input_manifest(output_dir: Path, doc_input: DocumentaryInput) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "input_type": doc_input.input_type,
        "raw_value": doc_input.raw_value,
        "topic": doc_input.topic,
        "youtube_url": doc_input.youtube_url,
        "duration_minutes": doc_input.duration_minutes,
        "folder_name": doc_input.folder_name,
        "series_id": doc_input.series_id,
        "has_supplemental": bool(doc_input.supplemental_text),
    }
    (output_dir / "input.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if doc_input.supplemental_text:
        (output_dir / "supplemental-input.txt").write_text(doc_input.supplemental_text, encoding="utf-8")
