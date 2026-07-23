#!/usr/bin/env python3
"""Derive overlay_hints.txt from scene.txt (shared across story types)."""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys
from typing import Any, Callable, Mapping

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DEEPSEEK_HELPER = REPO_ROOT / "crime-section" / "helper"

SCENE_HEADING_RE = re.compile(r"^--- Scene (\d+) / ~\d+ ---\s*$", re.MULTILINE)
NARRATION_LINE_INLINE_RE = re.compile(
    r"(?m)^(?:Hindi|English) line:[ \t]+(\S.+)$",
)
NARRATION_LINE_BLOCK_RE = re.compile(
    r"(?m)^(?:Hindi|English) line:\s*\n(.*?)\Z",
    re.DOTALL,
)

SYSTEM_PROMPT = """You extract short on-screen overlay hints from narration lines for a documentary video.

Rules:
- For each scene, output ONLY fields clearly present in the narration line.
- Allowed field types: date, location, person, organization, number, quote, question
- Use a short phrase from the line (not the full sentence).
- If nothing is worth highlighting, skip that scene entirely.
- Output plain text only — no markdown fences, no JSON, no commentary.

Output format (exactly):

Scene 1
date: 2025 की गर्मियों में

Scene 22
location: रॉचडेल शहर
date: 2000 से 2006 के बीच
"""


def parse_scene_txt(text: str) -> list[tuple[int, str]]:
    """Return (scene_number, narration_line) pairs from scene.txt."""
    headings = list(SCENE_HEADING_RE.finditer(text))
    if not headings:
        return []

    scenes: list[tuple[int, str]] = []
    for i, m in enumerate(headings):
        n = int(m.group(1))
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[start:end]

        inline = NARRATION_LINE_INLINE_RE.search(block)
        if inline:
            line = inline.group(1).strip()
        else:
            multiline = NARRATION_LINE_BLOCK_RE.search(block)
            line = multiline.group(1).strip() if multiline else ""

        if line:
            scenes.append((n, line))
    return scenes


def build_user_prompt(scenes: list[tuple[int, str]]) -> str:
    lines = ["Scenes to analyse:\n"]
    for n, narration in scenes:
        lines.append(f"Scene {n}: {narration}")
    lines.append(
        "\nWrite overlay hints using the format in your instructions. "
        "Skip scenes with nothing highlight-worthy."
    )
    return "\n".join(lines)


def overlay_hints_disabled() -> bool:
    return os.environ.get("DEEPSEEK_SKIP_OVERLAY_HINTS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def build_deepseek_client_kwargs() -> dict[str, Any]:
    """Build DeepSeek client kwargs using repo .env and INI defaults."""
    (
        bootstrap_deepseek_ini,
        build_client_kw,
        _call_deepseek,
        load_repo_dotenv,
        _log,
        resolve_api_key,
    ) = _load_deepseek_helpers()

    load_repo_dotenv(REPO_ROOT)

    ini_path = os.environ.get("DEEPSEEK_CONFIG_PATH")
    if ini_path:
        bootstrap_deepseek_ini(pathlib.Path(ini_path).expanduser())
    else:
        bootstrap_deepseek_ini(REPO_ROOT / "crime-section" / "deepseek.config.example.ini")

    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
    return build_client_kw(
        api_key=resolve_api_key(),
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        model=model,
        temperature=float(os.environ.get("DEEPSEEK_TEMPERATURE", "0")),
        reasoning_effort=os.environ.get("DEEPSEEK_REASONING_EFFORT"),
        enable_search=False,
        thinking=os.environ.get("DEEPSEEK_THINKING", "").strip().lower() in ("1", "true", "yes"),
    )


def generate_overlay_hints(
    scene_path: pathlib.Path,
    *,
    out_path: pathlib.Path | None = None,
    client_kwargs: Mapping[str, Any],
    call_llm: Callable[..., tuple[str, str | None]],
    batch_size: int = 50,
    force: bool = False,
    log: Callable[[str], None] | None = None,
) -> pathlib.Path | None:
    """Write overlay_hints.txt next to scene.txt (unless out_path is given)."""
    if not scene_path.is_file() or scene_path.stat().st_size == 0:
        if log:
            log(f"WARN: overlay hints skipped — {scene_path.name} missing or empty")
        return None

    hints_out = out_path or (scene_path.parent / "overlay_hints.txt")
    if hints_out.is_file() and hints_out.stat().st_size > 0 and not force:
        scene_mtime = scene_path.stat().st_mtime
        hints_mtime = hints_out.stat().st_mtime
        if scene_mtime <= hints_mtime:
            if log:
                log(
                    f"overlay hints: skipped ({hints_out.name} up to date; "
                    "use --force to redo)"
                )
            return hints_out

    text = scene_path.read_text(encoding="utf-8")
    scenes = parse_scene_txt(text)
    if not scenes:
        if log:
            log(f"WARN: overlay hints skipped — no scenes parsed from {scene_path.name}")
        return None

    max_tokens = int(os.environ.get("DEEPSEEK_MAX_TOKENS_OVERLAY", "16384"))
    parts: list[str] = []
    total_batches = max(1, (len(scenes) + batch_size - 1) // batch_size)

    for batch_idx, start in enumerate(range(0, len(scenes), batch_size), 1):
        batch = scenes[start : start + batch_size]
        label = f"overlay-hints {batch_idx}/{total_batches}"
        if log:
            log(f"overlay hints: calling DeepSeek for scenes {batch[0][0]}–{batch[-1][0]}...")
        user_prompt = build_user_prompt(batch)
        content, finish = call_llm(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            label=label,
            **client_kwargs,
        )
        if finish == "length":
            raise RuntimeError(
                f"{label} hit max_tokens ({max_tokens}). "
                "Raise DEEPSEEK_MAX_TOKENS_OVERLAY or lower overlay batch size."
            )
        cleaned = content.strip()
        if cleaned:
            parts.append(cleaned + "\n")

    merged = "\n".join(part.rstrip() for part in parts).strip() + "\n"
    hints_out.write_text(merged, encoding="utf-8")
    if log:
        log(f"overlay hints: wrote {hints_out.name} ({len(scenes)} scene(s) analysed)")
    return hints_out


def run_overlay_hints_for_scene(
    scene_path: pathlib.Path,
    *,
    out_path: pathlib.Path | None = None,
    client_kwargs: Mapping[str, Any] | None = None,
    call_llm: Callable[..., tuple[str, str | None]] | None = None,
    batch_size: int | None = None,
    force: bool = False,
    log: Callable[[str], None] | None = None,
) -> pathlib.Path | None:
    """Generate overlay_hints.txt after scene.txt — used by all story pipelines."""
    if overlay_hints_disabled():
        if log:
            log("overlay hints: skipped (DEEPSEEK_SKIP_OVERLAY_HINTS=1)")
        return None

    ck = client_kwargs or build_deepseek_client_kwargs()
    if call_llm is None:
        call_llm = _load_deepseek_helpers()[2]

    if batch_size is None:
        batch_size = max(1, int(os.environ.get("DEEPSEEK_OVERLAY_HINTS_BATCH", "50")))

    return generate_overlay_hints(
        scene_path,
        out_path=out_path,
        client_kwargs=ck,
        call_llm=call_llm,
        batch_size=batch_size,
        force=force,
        log=log,
    )


def _load_deepseek_helpers():
    sys.path.insert(0, str(DEEPSEEK_HELPER))
    from deepseek_pipeline import (  # noqa: WPS433
        bootstrap_deepseek_ini,
        build_client_kw,
        call_deepseek,
        load_repo_dotenv,
        log,
        resolve_api_key,
    )

    return (
        bootstrap_deepseek_ini,
        build_client_kw,
        call_deepseek,
        load_repo_dotenv,
        log,
        resolve_api_key,
    )


def main() -> int:
    p = argparse.ArgumentParser(
        description="Derive overlay_hints.txt from scene.txt via DeepSeek."
    )
    p.add_argument("--scene-txt", type=pathlib.Path, required=True)
    p.add_argument("--out", type=pathlib.Path, default=None)
    p.add_argument("--batch", type=int, default=50)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    try:
        run_overlay_hints_for_scene(
            args.scene_txt,
            out_path=args.out,
            batch_size=max(1, args.batch),
            force=args.force,
            log=_load_deepseek_helpers()[4],
        )
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
