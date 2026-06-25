#!/usr/bin/env python3
"""
generate_audio.py — standalone ElevenLabs TTS generator.

Easiest usage — paste any story path:

  ./elevenlabs-audio/run.sh general-story/story-to-run/ic-427-final
  ./elevenlabs-audio/run.sh /full/path/to/my-story.txt

The script stages the file under input/<slug>/FULL_STORY.txt and writes
MP3s to output/<slug>/.

Requires repo-root .env with ELEVENLABS_API_KEY (or eleven_labs_api_key).

Full narration mode splits FULL_STORY.txt into ``segment_count`` (default 6)
roughly equal parts at sentence boundaries. Each part is capped at ``max_chars``
(default 3500, including spaces) for the ElevenLabs API limit.
"""
from __future__ import annotations

import argparse
import configparser
import os
import re
import shutil
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

DEFAULT_VOICE_ID = "jHizw5Q9vzu8Pr4RakeJ"
DEFAULT_MODEL_ID = "eleven_v3"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_MAX_CHARS = 3500
DEFAULT_SEGMENT_COUNT = 6
DEFAULT_LANGUAGE_CODE = "hi"

SCENE_BLOCK_RE = re.compile(
    r"(?ms)^--- Scene (\d+) / ~\d+ ---\s*\nHindi line:\s*\n?(.*?)(?=\n\n--- Scene |\Z)"
)
SCENE_INLINE_RE = re.compile(
    r"(?ms)^--- Scene (\d+) / ~\d+ ---\s*\nHindi line:\s*(\S.*?)(?=\n\n--- Scene |\Z)"
)


def package_root() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    return package_root().parent


def log(msg: str) -> None:
    print(f"[elevenlabs] {msg}", flush=True)


def load_config(path: Path | None) -> dict[str, str]:
    defaults = {
        "voice_id": DEFAULT_VOICE_ID,
        "model_id": DEFAULT_MODEL_ID,
        "output_format": DEFAULT_OUTPUT_FORMAT,
        "max_chars": str(DEFAULT_MAX_CHARS),
        "segment_count": str(DEFAULT_SEGMENT_COUNT),
        "language_code": DEFAULT_LANGUAGE_CODE,
    }
    if not path or not path.is_file():
        return defaults

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    if not parser.has_section("elevenlabs"):
        return defaults

    section = parser["elevenlabs"]
    for key in defaults:
        if section.get(key):
            defaults[key] = section.get(key, defaults[key])
    return defaults


def require_api_key() -> str:
    for name in ("ELEVENLABS_API_KEY", "eleven_labs_api_key", "ELEVEN_LABS_API_KEY"):
        key = os.getenv(name, "").strip()
        if key:
            return key
    raise SystemExit(
        "Missing API key. Add ELEVENLABS_API_KEY to the repo-root .env file."
    )


def write_audio_stream(stream: Iterator[bytes], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as handle:
        for chunk in stream:
            if chunk:
                handle.write(chunk)


def supports_chunk_context(model_id: str) -> bool:
    """Some models (e.g. eleven_v3) reject previous_text / next_text."""
    return model_id not in {"eleven_v3", "eleven_v3_alpha"}


def convert_text(
    client: ElevenLabs,
    text: str,
    *,
    voice_id: str,
    model_id: str,
    output_format: str,
    language_code: str | None,
    previous_text: str | None = None,
    next_text: str | None = None,
) -> Iterator[bytes]:
    kwargs: dict = {
        "text": text,
        "voice_id": voice_id,
        "model_id": model_id,
        "output_format": output_format,
    }
    if language_code:
        kwargs["language_code"] = language_code
    if supports_chunk_context(model_id):
        if previous_text:
            kwargs["previous_text"] = previous_text
        if next_text:
            kwargs["next_text"] = next_text
    return client.text_to_speech.convert(**kwargs)


def sentence_units(text: str) -> list[str]:
    """Split story text into sentence-sized units (paragraph breaks preserved as unit gaps)."""
    units: list[str] = []
    for para in re.split(r"\n\s*\n", text.strip()):
        para = para.strip()
        if not para:
            continue
        for sent in re.split(r"(?<=[।.!?])\s+", para):
            sent = sent.strip()
            if sent:
                units.append(sent)
    return units


def split_into_equal_segments(
    text: str,
    num_segments: int = DEFAULT_SEGMENT_COUNT,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> list[str]:
    """Split narration into roughly equal parts; every part stays at or under max_chars."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    units = sentence_units(text)
    if not units:
        return chunk_text(text, max_chars)

    def join_units(parts: list[str]) -> str:
        return " ".join(parts)

    total = sum(len(u) for u in units) + max(0, len(units) - 1)
    min_parts = max(1, (total + max_chars - 1) // max_chars)
    n = max(num_segments, min_parts)
    target = total / n

    buckets: list[list[str]] = []
    current: list[str] = []
    current_len = 0

    for unit in units:
        add = len(unit) + (1 if current else 0)
        next_len = current_len + add
        should_split = bool(
            current
            and len(buckets) < n - 1
            and (
                next_len > max_chars
                or (current_len >= target * 0.85 and next_len > target)
            )
        )
        if should_split:
            buckets.append(current)
            current = [unit]
            current_len = len(unit)
        else:
            current.append(unit)
            current_len = next_len

    if current:
        buckets.append(current)

    segments = [join_units(bucket) for bucket in buckets if bucket]

    final: list[str] = []
    for seg in segments:
        if len(seg) <= max_chars:
            final.append(seg)
        else:
            final.extend(chunk_text(seg, max_chars))

    for index, seg in enumerate(final, start=1):
        if len(seg) > max_chars:
            raise ValueError(
                f"segment {index} is {len(seg)} chars (limit {max_chars} including spaces)"
            )

    return final


def chunk_text(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        if len(paragraph) <= max_chars:
            current = paragraph
            continue
        sentences = re.split(r"(?<=[।.!?])\s+", paragraph)
        buffer = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            candidate = f"{buffer} {sentence}".strip() if buffer else sentence
            if len(candidate) <= max_chars:
                buffer = candidate
                continue
            if buffer:
                chunks.append(buffer)
            if len(sentence) <= max_chars:
                buffer = sentence
            else:
                for i in range(0, len(sentence), max_chars):
                    chunks.append(sentence[i : i + max_chars])
                buffer = ""
        if buffer:
            current = buffer

    if current:
        chunks.append(current)
    return chunks


def parse_scene_lines(scene_path: Path) -> list[tuple[int, str]]:
    text = scene_path.read_text(encoding="utf-8")
    scenes: dict[int, str] = {}

    for match in SCENE_BLOCK_RE.finditer(text):
        scene_num = int(match.group(1))
        line = " ".join(match.group(2).strip().split())
        if line:
            scenes[scene_num] = line

    for match in SCENE_INLINE_RE.finditer(text):
        scene_num = int(match.group(1))
        line = " ".join(match.group(2).strip().split())
        if line and scene_num not in scenes:
            scenes[scene_num] = line

    if not scenes:
        raise ValueError(f"no scenes found in {scene_path}")

    return sorted(scenes.items())


def resolve_input(slug: str, source_dir: Path | None) -> tuple[Path, Path | None]:
    """Return (source_path, text_file_or_none).

    source_path is a folder (FULL_STORY.txt / scene.txt) or a plain text file.
    When a plain file is returned, text_file is set and full/scenes modes read it directly.
    """
    if source_dir:
        resolved = source_dir.expanduser().resolve()
        if resolved.is_file():
            return resolved, resolved
        if not resolved.is_dir():
            raise FileNotFoundError(f"source path not found: {resolved}")
        return resolved, None

    local = package_root() / "input" / slug
    if local.is_file():
        return local, local
    if local.is_dir():
        return local, None

    raise FileNotFoundError(
        f"input not found: {local}\n"
        f"Add a text file at input/{slug} or a folder input/{slug}/FULL_STORY.txt, "
        f"or pass --source-dir."
    )


def resolve_output_dir(slug: str | None, output_dir: Path | None) -> Path:
    if output_dir:
        return output_dir.expanduser().resolve()
    if slug:
        return package_root() / "output" / slug
    return package_root() / "output" / "inline"


def slug_from_path(path: Path) -> str:
    name = path.stem if path.is_file() else path.name
    slug = re.sub(r"[^a-zA-Z0-9\-_]", "-", name)
    slug = re.sub(r"-+", "-", slug).strip("-").lower()
    return slug or "story"


def find_story_file(path: Path) -> Path:
    if path.is_file():
        return path
    if not path.is_dir():
        raise FileNotFoundError(f"story path not found: {path}")

    for name in ("FULL_STORY.txt", "full_story.txt", "story.txt"):
        candidate = path / name
        if candidate.is_file():
            return candidate

    text_files = sorted(
        f for f in path.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.suffix.lower() != ".mp3"
    )
    if len(text_files) == 1:
        return text_files[0]
    if text_files:
        names = ", ".join(f.name for f in text_files[:5])
        raise FileNotFoundError(
            f"folder has multiple files — add FULL_STORY.txt or pass a file path. Found: {names}"
        )
    raise FileNotFoundError(f"no story file found in {path}")


def stage_story(story_path: Path) -> tuple[str, Path, Path]:
    """Copy story into input/<slug>/ and return slug, staged file, output dir."""
    source = story_path.expanduser().resolve()
    story_file = find_story_file(source)
    slug = slug_from_path(story_file)

    input_dir = package_root() / "input" / slug
    input_dir.mkdir(parents=True, exist_ok=True)
    staged = input_dir / "FULL_STORY.txt"

    if story_file.resolve() != staged.resolve():
        shutil.copy2(story_file, staged)
        log(f"staged input → {staged}")
    else:
        log(f"using input → {staged}")

    out_dir = package_root() / "output" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    log(f"output → {out_dir}")
    return slug, staged, out_dir


def generate_full_narration(
    client: ElevenLabs,
    text: str,
    out_dir: Path,
    *,
    voice_id: str,
    model_id: str,
    output_format: str,
    language_code: str | None,
    max_chars: int,
    segment_count: int,
    play: bool,
) -> list[Path]:
    chunks = split_into_equal_segments(text, num_segments=segment_count, max_chars=max_chars)
    if not chunks:
        raise ValueError("no text to convert")

    min_parts = max(1, (len(text.strip()) + max_chars - 1) // max_chars)
    if min_parts > segment_count:
        log(
            f"story needs {min_parts} part(s) to stay under {max_chars} chars each "
            f"(target was {segment_count} equal segments)"
        )
    else:
        log(
            f"split into {len(chunks)} equal segment(s) "
            f"(target {segment_count}, max {max_chars} chars each incl. spaces)"
        )

    if len(chunks) > 1 and not supports_chunk_context(model_id):
        log(f"{model_id} does not support cross-chunk context (previous_text/next_text)")

    written: list[Path] = []
    for index, chunk in enumerate(chunks, start=1):
        previous = chunks[index - 2] if index > 1 else None
        next_chunk = chunks[index] if index < len(chunks) else None
        name = "full_narration.mp3" if len(chunks) == 1 else f"full_narration_part_{index:03d}.mp3"
        dest = out_dir / name
        log(f"generating {dest.name} ({len(chunk)} chars)")
        stream = convert_text(
            client,
            chunk,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            language_code=language_code,
            previous_text=previous,
            next_text=next_chunk,
        )
        write_audio_stream(stream, dest)
        written.append(dest)

    if play and written:
        try:
            from elevenlabs.play import play

            play(written[-1].read_bytes())
        except Exception as exc:  # noqa: BLE001
            log(f"playback skipped: {exc}")

    return written


def generate_scene_audio(
    client: ElevenLabs,
    scenes: list[tuple[int, str]],
    out_dir: Path,
    *,
    voice_id: str,
    model_id: str,
    output_format: str,
    language_code: str | None,
    start: int | None,
    end: int | None,
    skip_existing: bool,
) -> list[Path]:
    written: list[Path] = []
    for scene_num, line in scenes:
        if start is not None and scene_num < start:
            continue
        if end is not None and scene_num > end:
            continue

        dest = out_dir / f"scene_{scene_num:03d}.mp3"
        if skip_existing and dest.is_file() and dest.stat().st_size > 0:
            log(f"skip existing {dest.name}")
            written.append(dest)
            continue

        log(f"generating {dest.name} ({len(line)} chars)")
        stream = convert_text(
            client,
            line,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            language_code=language_code,
        )
        write_audio_stream(stream, dest)
        written.append(dest)

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate ElevenLabs narration audio (standalone package)."
    )
    parser.add_argument(
        "story_path",
        nargs="?",
        type=Path,
        help="Path to story file or folder — auto-creates input/<slug>/ and output/<slug>/",
    )
    parser.add_argument(
        "--story-path",
        type=Path,
        dest="story_path_flag",
        help="Same as positional story path",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="INI config (default: elevenlabs-audio/config.example.ini)",
    )
    parser.add_argument(
        "--slug",
        help="Episode name — reads input/<slug>/, writes output/<slug>/",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Override input folder (e.g. general-story/stories/cockroach)",
    )
    parser.add_argument(
        "--mode",
        choices=("full", "scenes", "file"),
        default="full",
        help="full = FULL_STORY.txt, scenes = scene.txt, file = --input path",
    )
    parser.add_argument("--input", type=Path, help="Custom text file for --mode file")
    parser.add_argument("--text", help="Inline text (ignores --slug/--mode)")
    parser.add_argument("--output-dir", type=Path, help="Override output directory")
    parser.add_argument("--voice-id", help="ElevenLabs voice_id")
    parser.add_argument("--model-id", help="ElevenLabs model_id")
    parser.add_argument("--output-format", help="e.g. mp3_44100_128")
    parser.add_argument("--language-code", help="ISO 639-1 code, e.g. hi or en")
    parser.add_argument(
        "--max-chars",
        type=int,
        help=f"Max chars per segment incl. spaces (default {DEFAULT_MAX_CHARS}, ElevenLabs limit)",
    )
    parser.add_argument(
        "--chunk-chars",
        type=int,
        help="Alias for --max-chars (deprecated)",
    )
    parser.add_argument(
        "--segment-count",
        type=int,
        default=None,
        help=f"Target number of equal narration segments (default {DEFAULT_SEGMENT_COUNT})",
    )
    parser.add_argument("--scene-start", type=int, help="First scene number (inclusive)")
    parser.add_argument("--scene-end", type=int, help="Last scene number (inclusive)")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="In scenes mode, skip MP3s that already exist",
    )
    parser.add_argument("--play", action="store_true", help="Play the last generated clip")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    load_dotenv(repo_root() / ".env")
    cfg_path = args.config or (package_root() / "config.example.ini")
    cfg = load_config(cfg_path)

    voice_id = args.voice_id or cfg["voice_id"]
    model_id = args.model_id or cfg["model_id"]
    output_format = args.output_format or cfg["output_format"]
    language_code = args.language_code or cfg["language_code"] or None
    max_chars = (
        args.max_chars
        or args.chunk_chars
        or int(cfg.get("max_chars") or cfg.get("chunk_chars") or DEFAULT_MAX_CHARS)
    )
    segment_count = (
        args.segment_count
        if args.segment_count is not None
        else int(cfg.get("segment_count", DEFAULT_SEGMENT_COUNT))
    )

    client = ElevenLabs(api_key=require_api_key())

    story_path = args.story_path_flag or args.story_path
    if story_path:
        source = story_path.expanduser().resolve()
        story_file = find_story_file(source)
        if args.output_dir:
            out_dir = args.output_dir.expanduser().resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            log(f"reading → {story_file}")
            log(f"output → {out_dir}")
            text = story_file.read_text(encoding="utf-8")
        else:
            _, staged, out_dir = stage_story(source)
            text = staged.read_text(encoding="utf-8")
        written = generate_full_narration(
            client,
            text,
            out_dir,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            language_code=language_code,
            max_chars=max_chars,
            segment_count=segment_count,
            play=args.play,
        )
        log(f"done — {len(written)} file(s) in {out_dir}")
        return 0

    if args.text:
        out_dir = resolve_output_dir(None, args.output_dir)
        written = generate_full_narration(
            client,
            args.text,
            out_dir,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            language_code=language_code,
            max_chars=max_chars,
            segment_count=segment_count,
            play=args.play,
        )
        log(f"done — {len(written)} file(s) in {out_dir}")
        return 0

    if args.mode == "file":
        if not args.input:
            parser.error("--mode file requires --input")
        source_path = args.input.expanduser().resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"missing input file: {source_path}")
        text = source_path.read_text(encoding="utf-8")
        slug = args.slug or source_path.stem
        out_dir = resolve_output_dir(slug, args.output_dir)
        written = generate_full_narration(
            client,
            text,
            out_dir,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            language_code=language_code,
            max_chars=max_chars,
            segment_count=segment_count,
            play=args.play,
        )
        log(f"done — {len(written)} file(s) in {out_dir}")
        return 0

    if not args.slug:
        parser.error("--slug is required unless --text or --mode file with --input is used")

    source_path, text_file = resolve_input(args.slug, args.source_dir)
    out_dir = resolve_output_dir(args.slug, args.output_dir)

    if args.mode == "scenes":
        scene_path = text_file if text_file and text_file.name == "scene.txt" else source_path / "scene.txt"
        if text_file and text_file.name != "scene.txt" and text_file.is_file():
            raise FileNotFoundError(
                f"scenes mode needs scene.txt — got plain file: {text_file}"
            )
        if not scene_path.is_file():
            raise FileNotFoundError(f"missing {scene_path}")
        scenes = parse_scene_lines(scene_path)
        written = generate_scene_audio(
            client,
            scenes,
            out_dir,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            language_code=language_code,
            start=args.scene_start,
            end=args.scene_end,
            skip_existing=args.skip_existing,
        )
        log(f"done — {len(written)} scene file(s) in {out_dir}")
        return 0

    if text_file and text_file.is_file():
        text = text_file.read_text(encoding="utf-8")
    else:
        full_story_path = source_path / "FULL_STORY.txt"
        if not full_story_path.is_file():
            raise FileNotFoundError(f"missing {full_story_path}")
        text = full_story_path.read_text(encoding="utf-8")
    written = generate_full_narration(
        client,
        text,
        out_dir,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format,
        language_code=language_code,
        max_chars=max_chars,
        segment_count=segment_count,
        play=args.play,
    )
    log(f"done — {len(written)} file(s) in {out_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        log("interrupted")
        raise SystemExit(130) from None
