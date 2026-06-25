#!/usr/bin/env python3
"""
export_prompt_derivatives.py — derive scene.txt and image-prompts-only.txt from prompt.txt.

Reads Stage C ``prompt.txt`` blocks (``--- Scene N / ~M ---``) and writes:

  • scene.txt — scene headings + Hindi lines only
  • image-prompts-only.txt — one IMAGE PROMPT line per scene
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Callable

HINDI_LINE_RE = re.compile(
    r"(?m)^Hindi line:\s*\n(.*?)(?=\n(?:IMAGE PROMPT|DIGEN MOTION PROMPT|--- Scene|\Z))",
    re.DOTALL,
)

IMAGE_PROMPT_RE = re.compile(
    r"(?m)^IMAGE PROMPT\s*\n(.*?)(?=\n(?:DIGEN MOTION PROMPT|--- Scene|\Z))",
    re.DOTALL,
)

_SCENE_HEADING_LINE = re.compile(
    r"^--- Scene \d+ / ~\d+ ---\s*$",
    re.MULTILINE,
)


def _collapse_line(text: str) -> str:
    return " ".join(text.strip().split())


def extract_hindi_line(block: str) -> str:
    m = HINDI_LINE_RE.search(block)
    if not m:
        return ""
    return m.group(1).strip()


def extract_image_prompt(block: str) -> str:
    m = IMAGE_PROMPT_RE.search(block)
    if not m:
        return ""
    return _collapse_line(m.group(1))


def extract_scene_heading(block: str) -> str:
    first_line = block.strip().splitlines()[0] if block.strip() else ""
    return first_line.strip()


def extract_hindi_line_inline(block: str) -> str | None:
    m = re.search(r"(?m)^Hindi line:[ \t]+(\S.+)$", block)
    if not m:
        return None
    return m.group(1).strip()


def format_scene_entry(block: str) -> str | None:
    heading = extract_scene_heading(block)
    if not heading or not _SCENE_HEADING_LINE.match(heading):
        return None
    inline = extract_hindi_line_inline(block)
    if inline is not None:
        return f"{heading}\nHindi line: {inline}\n"
    hindi = extract_hindi_line(block)
    return f"{heading}\nHindi line:\n{hindi}\n"


def build_scene_txt(blocks: dict[int, str]) -> str:
    parts: list[str] = []
    for n in sorted(blocks):
        entry = format_scene_entry(blocks[n])
        if not entry:
            continue
        parts.append(entry)
        if "\nHindi line:\n" in entry:
            parts.append("\n")
    return "".join(parts)


def build_image_prompts_only(blocks: dict[int, str]) -> str:
    lines: list[str] = []
    for n in sorted(blocks):
        prompt = extract_image_prompt(blocks[n])
        if prompt:
            lines.append(prompt)
    return "\n".join(lines) + ("\n" if lines else "")


def export_prompt_derivatives(
    prompt_path: pathlib.Path,
    *,
    scene_path: pathlib.Path | None = None,
    image_prompts_path: pathlib.Path | None = None,
    split_blocks: Callable[[str], dict[int, str]],
    log: Callable[[str], None] | None = None,
) -> tuple[pathlib.Path, pathlib.Path]:
    """Write derivative files next to prompt.txt unless explicit paths are given."""
    if not prompt_path.is_file():
        raise FileNotFoundError(f"missing prompt file: {prompt_path}")

    story_dir = prompt_path.parent
    scene_out = scene_path or (story_dir / "scene.txt")
    image_out = image_prompts_path or (story_dir / "image-prompts-only.txt")

    text = prompt_path.read_text(encoding="utf-8")
    blocks = split_blocks(text)
    if not blocks:
        raise ValueError(f"no scene blocks found in {prompt_path}")

    scene_text = build_scene_txt(blocks)
    image_text = build_image_prompts_only(blocks)

    scene_out.write_text(scene_text, encoding="utf-8")
    image_out.write_text(image_text, encoding="utf-8")

    if log:
        log(
            f"exported {len(blocks)} scene(s) → {scene_out.name}, "
            f"{image_text.count(chr(10)) or len(blocks)} image prompt line(s) → {image_out.name}"
        )

    return scene_out, image_out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prompt", type=pathlib.Path, required=True, help="Path to prompt.txt")
    p.add_argument("--scene-out", type=pathlib.Path, default=None)
    p.add_argument("--image-prompts-out", type=pathlib.Path, default=None)
    args = p.parse_args()

    # Import split helper from the shared pipeline module.
    repo_root = pathlib.Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(repo_root / "crime-section" / "helper"))
    from deepseek_pipeline import log, split_stage_c_prompt_blocks  # noqa: WPS433

    try:
        export_prompt_derivatives(
            args.prompt,
            scene_path=args.scene_out,
            image_prompts_path=args.image_prompts_out,
            split_blocks=split_stage_c_prompt_blocks,
            log=log,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
