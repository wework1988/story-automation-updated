#!/usr/bin/env python3
"""Generate text-overlay.txt from scene.txt using the master overlay selector prompt."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

from overlay_hints import (
    REPO_ROOT,
    build_deepseek_client_kwargs,
    parse_scene_txt,
    _load_deepseek_helpers,
)

MASTER_PROMPT_PATH = (
    REPO_ROOT / "story-making-prompts" / "text-overlay-from -scene.txt"
)
SCENE_PLACEHOLDER = "[PASTE SCENES HERE]"
OUTPUT_LINE_RE = re.compile(
    r"^\s*(?:\*\*)?Scene\s+(\d+)\s*(?:\*\*)?\s*:\s*(.+?)\s*$",
    re.IGNORECASE,
)


def load_master_prompt() -> str:
    if not MASTER_PROMPT_PATH.is_file():
        sys.exit(f"error: missing master prompt {MASTER_PROMPT_PATH}")
    text = MASTER_PROMPT_PATH.read_text(encoding="utf-8")
    if SCENE_PLACEHOLDER not in text:
        sys.exit(f"error: {SCENE_PLACEHOLDER!r} not found in master prompt")
    return text.split("---", 1)[0].strip()


def format_scenes_block(scenes: list[tuple[int, str]]) -> str:
    lines = []
    for n, narration in scenes:
        lines.append(f"--- Scene {n} ---")
        lines.append(f"Hindi line: {narration}")
        lines.append("")
    return "\n".join(lines).strip()


def build_user_prompt(master: str, scenes: list[tuple[int, str]]) -> str:
    block = format_scenes_block(scenes)
    cap = 12 if scenes[0][0] <= 20 else 6
    tail = (
        f"\n\nAnalyse scenes {scenes[0][0]}–{scenes[-1][0]} only. "
        f"Reply with at most {cap} overlay lines. "
        "Start your reply immediately with the first Scene line — no preamble."
    )
    return master.replace(SCENE_PLACEHOLDER, block) + tail


def parse_overlay_lines(text: str) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for line in text.splitlines():
        line = line.strip().lstrip("-*•").strip()
        if not line or line.startswith("#"):
            continue
        m = OUTPUT_LINE_RE.match(line)
        if m:
            overlay = m.group(2).strip().strip("*")
            rows.append((int(m.group(1)), overlay))
    if rows:
        return rows
    # Fallback: scan for inline Scene N: patterns anywhere in the blob.
    for m in re.finditer(r"(?m)^Scene\s+(\d+)\s*:\s*(.+)$", text):
        rows.append((int(m.group(1)), m.group(2).strip().strip("*")))
    return rows


def generate_text_overlay(
    scene_path: pathlib.Path,
    *,
    out_path: pathlib.Path | None = None,
    batch_size: int = 60,
    force: bool = False,
) -> pathlib.Path:
    import os

    os.environ.setdefault("DEEPSEEK_THINKING", "0")
    os.environ.pop("DEEPSEEK_REASONING_EFFORT", None)
    os.environ.setdefault("DEEPSEEK_MODEL", "deepseek-chat")

    log = _load_deepseek_helpers()[4]
    call_llm = _load_deepseek_helpers()[2]
    client_kwargs = build_deepseek_client_kwargs()
    client_kwargs["model"] = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    client_kwargs["thinking"] = False
    client_kwargs["reasoning_effort"] = None

    if not scene_path.is_file():
        sys.exit(f"error: scene file not found: {scene_path}")

    out = out_path or (scene_path.parent / "text-overlay.txt")
    if out.is_file() and out.stat().st_size > 0 and not force:
        if out.stat().st_mtime >= scene_path.stat().st_mtime:
            log(f"text-overlay: skipped ({out.name} up to date; use --force to redo)")
            return out

    scenes = parse_scene_txt(scene_path.read_text(encoding="utf-8"))
    if not scenes:
        sys.exit(f"error: no scenes parsed from {scene_path}")

    master = load_master_prompt()
    max_tokens = int(os.environ.get("DEEPSEEK_MAX_TOKENS_OVERLAY", "1024"))
    all_rows: list[tuple[int, str]] = []
    total_batches = max(1, (len(scenes) + batch_size - 1) // batch_size)

    for batch_idx, start in enumerate(range(0, len(scenes), batch_size), 1):
        batch = scenes[start : start + batch_size]
        label = f"text-overlay {batch_idx}/{total_batches}"
        log(f"text-overlay: DeepSeek scenes {batch[0][0]}–{batch[-1][0]}...")
        user_prompt = build_user_prompt(master, batch)
        content, finish = call_llm(
            system_prompt=(
                "You are a YouTube documentary overlay selector. "
                "Output ONLY lines exactly like: Scene 12: overlay text "
                "(one scene per line, no markdown, no bullets, no explanations, no reasoning). "
                "Follow the user's frequency rules strictly — most batches need only 3–8 lines."
            ),
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            label=label,
            **client_kwargs,
        )
        parsed = parse_overlay_lines(content)
        if finish == "length":
            if parsed:
                log(
                    f"WARN: {label} hit max_tokens but salvaged {len(parsed)} overlay line(s)"
                )
            else:
                raise RuntimeError(
                    f"{label} hit max_tokens ({max_tokens}) with no parseable lines. "
                    "Raise DEEPSEEK_MAX_TOKENS_OVERLAY or lower --batch."
                )
        elif not parsed:
            log(f"WARN: {label} returned no parseable overlay lines")
        all_rows.extend(parsed)

    # Dedupe by scene number (keep first); sort by scene.
    seen: set[int] = set()
    unique: list[tuple[int, str]] = []
    for n, text in sorted(all_rows, key=lambda x: x[0]):
        if n in seen:
            continue
        seen.add(n)
        unique.append((n, text))

    body = "\n".join(f"Scene {n}: {text}" for n, text in unique) + "\n"
    out.write_text(body, encoding="utf-8")
    log(f"text-overlay: wrote {out} ({len(unique)} overlay(s) from {len(scenes)} scenes)")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Generate text-overlay.txt from scene.txt")
    p.add_argument("--scene-txt", type=pathlib.Path, required=True)
    p.add_argument("--out", type=pathlib.Path, default=None)
    p.add_argument("--batch", type=int, default=60)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    try:
        generate_text_overlay(
            args.scene_txt,
            out_path=args.out,
            batch_size=max(1, args.batch),
            force=args.force,
        )
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
