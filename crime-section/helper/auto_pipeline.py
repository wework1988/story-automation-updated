#!/usr/bin/env python3
"""
auto_pipeline.py — run Stage A + Stage B + Stage C end-to-end against
Claude (Anthropic SDK) with prompt caching for cost optimization.

Invoked by helper/create-story-skelton-auto when STAGE=auto.

Cost model (prompt caching only):
- Stage A: 1 call. Static spec is sent once and cached on creation.
- Stage B: 1 call. Same — cache write only.
- Stage C: N batch calls (~10–20 typical). Two cached system blocks:
    block 1 = static Stage C spec (PART 1 + PART 2)
    block 2 = STORY_CONFIG_BLOCK + LOCKED_SCENE_BREAKDOWN + CHARACTER_LIBRARY
  Only SCENE_RANGE varies per call — turning calls 2..N into mostly cache reads.

Outputs are written to:
- stories/<name>/output_config_<name>.md            (Stage A)
- stories/<name>/output_story_breakdown_<name>.md   (Stage B)
- stories/<name>/prompt.txt                         (Stage C aggregated)

The bifurcated template files in stories/<name>/template/ are also kept
mirror-updated (matching what step2/step3/step4 do manually) for traceability.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys
import time
from typing import Optional


# ---------- placeholder strings (must match the bifuracted-template files) ----

PH_FULL_STORY_A = "{Paste the full Hindi / Hinglish / English story here.}"
PH_FULL_STORY_B = "{Paste the full Hindi / Hinglish / English story here — same as used in Stage A.}"
PH_GENRE = "{Paste optional genre or tone hint here, or leave blank.}"
PH_CONFIG = "{Paste the STORY CONFIG BLOCK output from Stage A here.}"
PH_BREAKDOWN = "{Paste the LOCKED SCENE BREAKDOWN output from Stage B here.}"
PH_SCENE_RANGE = (
    '{Example: "Scenes 1–10". Specify the scenes to generate IMAGE PROMPT '
    "+ DIGEN MOTION PROMPT for in this call.}"
)

# Multi-line CHARACTER_LIBRARY placeholders (matched as a regex because the
# wrapping text differs slightly between stages).
CHAR_LIB_RE = re.compile(
    r"\{Paste (?:the full contents of the locked character library|the same locked character library text)[^}]*\}",
    re.DOTALL,
)

PART3_MARKER = "PART 3 — INPUT SLOTS"


# ---------- small helpers --------------------------------------------------


def log(msg: str) -> None:
    print(f"[auto] {msg}", flush=True)


def read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: pathlib.Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")


def split_at_part3(template_text: str) -> tuple[str, str]:
    """Return (cached_static_prefix, variable_suffix). Suffix begins at PART3_MARKER."""
    idx = template_text.find(PART3_MARKER)
    if idx < 0:
        sys.exit(f"error: '{PART3_MARKER}' not found in template")
    # Walk back to the start of the equals-sign separator above the marker so
    # the cached prefix ends on a clean section boundary.
    start = template_text.rfind("\n", 0, idx)
    if start < 0:
        start = idx
    sep_above = template_text.rfind("=" * 40, 0, start)
    if sep_above >= 0:
        # find the line above that equals separator
        line_start = template_text.rfind("\n", 0, sep_above)
        if line_start >= 0:
            cut = line_start + 1
        else:
            cut = sep_above
    else:
        cut = start + 1
    return template_text[:cut], template_text[cut:]


def replace_one(haystack: str, needle: str, replacement: str, label: str) -> str:
    if needle not in haystack:
        sys.exit(f"error: placeholder missing ({label}): {needle[:80]}...")
    return haystack.replace(needle, replacement, 1)


def replace_char_lib(haystack: str, replacement: str) -> str:
    new, n = CHAR_LIB_RE.subn(replacement, haystack, count=1)
    if n == 0:
        sys.exit("error: CHARACTER_LIBRARY placeholder not found")
    return new


def parse_scene_count(stage_b_output: str) -> int:
    """Find the highest 'Scene <N>' marker in the Stage B output."""
    nums = [int(m.group(1)) for m in re.finditer(r"\bScene\s+(\d+)\b", stage_b_output)]
    return max(nums) if nums else 0


def parse_next_range_start(text: str) -> Optional[int]:
    """Extract starting scene from a trailing 'NEXT_RANGE: Scenes X–Y' line."""
    m = re.search(
        r"NEXT_RANGE:\s*Scenes?\s+(\d+)\s*[–\-]\s*\d+",
        text,
        re.IGNORECASE,
    )
    return int(m.group(1)) if m else None


def strip_trailing_next_range(text: str) -> str:
    return re.sub(
        r"\n*NEXT_RANGE:\s*Scenes?\s+\d+\s*[–\-]\s*\d+\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )


# ---------- Anthropic call wrapper -----------------------------------------


def make_client():
    import anthropic  # imported lazily so --help works without the package

    return anthropic.Anthropic()


def call_claude(
    client,
    *,
    model: str,
    system_blocks: list[dict],
    user_text: str,
    max_tokens: int,
    label: str,
    temperature: float = 0.0,
) -> str:
    """Call messages.create with cached system blocks; return full text response."""
    t0 = time.time()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_blocks,
        messages=[{"role": "user", "content": user_text}],
    )
    dt = time.time() - t0

    # Concatenate all text parts of the response.
    parts: list[str] = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    text = "".join(parts)

    u = resp.usage
    cache_read = getattr(u, "cache_read_input_tokens", 0) or 0
    cache_create = getattr(u, "cache_creation_input_tokens", 0) or 0
    log(
        f"[{label}] input={u.input_tokens} cache_read={cache_read} "
        f"cache_create={cache_create} output={u.output_tokens} "
        f"stop={resp.stop_reason} {dt:.1f}s"
    )
    if resp.stop_reason == "max_tokens":
        log(f"[{label}] WARNING: stop_reason=max_tokens, output may be truncated")
    return text


def make_cached_block(text: str) -> dict:
    return {
        "type": "text",
        "text": text,
        "cache_control": {"type": "ephemeral"},
    }


# ---------- stage runners --------------------------------------------------


def run_stage_a(
    client,
    *,
    model: str,
    template_path: pathlib.Path,
    full_story: str,
    character_lib: str,
    genre: str,
    out_path: pathlib.Path,
    template_mirror_path: pathlib.Path,
) -> str:
    template = read(template_path)
    static_prefix, variable_suffix = split_at_part3(template)

    body = variable_suffix
    body = replace_one(body, PH_FULL_STORY_A, full_story, "FULL_STORY (A)")
    body = replace_one(body, PH_GENRE, genre, "OPTIONAL_GENRE_OR_TONE")
    body = replace_char_lib(body, character_lib)

    write(template_mirror_path, static_prefix + body)

    log("Stage A: calling model...")
    out = call_claude(
        client,
        model=model,
        system_blocks=[make_cached_block(static_prefix)],
        user_text=body,
        max_tokens=8000,
        label="stage-a",
    )
    out = out.strip() + "\n"
    write(out_path, out)
    log(f"Stage A: wrote {out_path}")
    return out


def run_stage_b(
    client,
    *,
    model: str,
    template_path: pathlib.Path,
    config_block: str,
    full_story: str,
    character_lib: str,
    out_path: pathlib.Path,
    template_mirror_path: pathlib.Path,
) -> str:
    template = read(template_path)
    static_prefix, variable_suffix = split_at_part3(template)

    body = variable_suffix
    body = replace_one(body, PH_CONFIG, config_block, "STORY_CONFIG_BLOCK (B)")
    body = replace_one(body, PH_FULL_STORY_B, full_story, "FULL_STORY (B)")
    body = replace_char_lib(body, character_lib)

    write(template_mirror_path, static_prefix + body)

    log("Stage B: calling model...")
    out = call_claude(
        client,
        model=model,
        system_blocks=[make_cached_block(static_prefix)],
        user_text=body,
        max_tokens=16000,
        label="stage-b",
    )
    out = out.strip() + "\n"
    write(out_path, out)
    log(f"Stage B: wrote {out_path}")
    return out


def run_stage_c(
    client,
    *,
    model: str,
    template_path: pathlib.Path,
    config_block: str,
    breakdown: str,
    character_lib: str,
    batch_size: int,
    out_path: pathlib.Path,
    template_mirror_path: pathlib.Path,
) -> None:
    template = read(template_path)
    static_prefix, variable_suffix = split_at_part3(template)

    total = parse_scene_count(breakdown)
    if total <= 0:
        sys.exit("error: could not detect any 'Scene <N>' markers in Stage B output")
    log(f"Stage C: detected {total} scenes; batch size = {batch_size}")

    # Split the variable suffix into "context" (config + breakdown + char lib)
    # and "scene-range tail" so the context can be its own cache breakpoint.
    body_pre = variable_suffix
    body_pre = replace_one(body_pre, PH_CONFIG, config_block, "STORY_CONFIG_BLOCK (C)")
    body_pre = replace_one(body_pre, PH_BREAKDOWN, breakdown, "LOCKED_SCENE_BREAKDOWN (C)")
    body_pre = replace_char_lib(body_pre, character_lib)

    # Carve out everything from the SCENE_RANGE: line through the end of the file.
    sr_idx = body_pre.find("SCENE_RANGE:")
    if sr_idx < 0:
        sys.exit("error: 'SCENE_RANGE:' label not found in Stage C template")
    cached_context = body_pre[:sr_idx]
    scene_range_tail = body_pre[sr_idx:]

    if PH_SCENE_RANGE not in scene_range_tail:
        sys.exit("error: SCENE_RANGE placeholder not found")

    # Mirror first-batch fill to disk for traceability.
    first_filled = static_prefix + body_pre.replace(
        PH_SCENE_RANGE, f"Scenes 1-{min(batch_size, total)}", 1
    )
    write(template_mirror_path, first_filled)

    # Wipe the destination file at the start so a clean append-loop produces
    # a coherent file. The bash wrapper's --force / resume guard already gated this.
    write(out_path, "")

    cur = 1
    batch_idx = 0
    estimated_batches = max(1, (total + batch_size - 1) // batch_size)
    while cur <= total:
        batch_idx += 1
        end = min(cur + batch_size - 1, total)
        scene_range = f"Scenes {cur}-{end}"
        user_text = scene_range_tail.replace(PH_SCENE_RANGE, scene_range, 1)

        label = f"stage-c {batch_idx}/{estimated_batches} ({scene_range})"
        log(f"Stage C: calling model for {scene_range}...")

        text = call_claude(
            client,
            model=model,
            system_blocks=[
                make_cached_block(static_prefix),
                make_cached_block(cached_context),
            ],
            user_text=user_text,
            max_tokens=16000,
            label=label,
        )

        next_start = parse_next_range_start(text)
        clean = strip_trailing_next_range(text).rstrip() + "\n\n"

        with out_path.open("a", encoding="utf-8") as f:
            f.write(clean)

        # Decide next window start.
        if next_start is not None and cur < next_start <= end + 1:
            log(f"Stage C: model emitted NEXT_RANGE; resuming at scene {next_start}")
            cur = next_start
        else:
            cur = end + 1

    log(f"Stage C: complete; wrote {out_path}")


# ---------- main -----------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--story", required=True, help="story slug, e.g. operation-bandar")
    p.add_argument("--root", required=True, help="repo root (parent of stories/ and bifuracted-template/)")
    p.add_argument("--model", default="claude-opus-4-7")
    p.add_argument("--batch", type=int, default=8, help="scenes per Stage C call")
    p.add_argument("--use-character-lib", action="store_true",
                   help="inject template/character.txt into CHARACTER_LIBRARY: slots")
    p.add_argument("--force", action="store_true",
                   help="re-run stages even if output files are non-empty")
    p.add_argument("--genre", default="", help="OPTIONAL_GENRE_OR_TONE hint for Stage A")
    args = p.parse_args()

    root = pathlib.Path(args.root).resolve()
    story = args.story
    story_dir = root / "stories" / story
    tmpl_dir = story_dir / "template"
    src_tmpl_dir = root / "bifuracted-template"

    full_path = story_dir / "FULL_STORY.txt"
    config_path = story_dir / f"output_config_{story}.md"
    breakdown_path = story_dir / f"output_story_breakdown_{story}.md"
    prompt_path = story_dir / "prompt.txt"

    a_template = src_tmpl_dir / "stage-a-story-config.md"
    b_template = src_tmpl_dir / "stage-b-scene-breakdown.md"
    c_template = src_tmpl_dir / "stage-c-image-motion.md"

    a_mirror = tmpl_dir / f"STORY_Config_{story}.md"
    b_mirror = tmpl_dir / f"Story_scene_breakdown_{story}.md"
    c_mirror = tmpl_dir / f"{story}_stage-c-image-motion.md"

    for required in (full_path, a_template, b_template, c_template):
        if not required.is_file():
            sys.exit(f"error: missing {required}")

    full_story = read(full_path).strip()
    if not full_story:
        sys.exit(f"error: {full_path} is empty")

    # Resolve CHARACTER_LIBRARY content.
    if args.use_character_lib:
        char_path = tmpl_dir / "character.txt"
        if char_path.is_file() and char_path.stat().st_size > 0:
            character_lib = read(char_path).strip()
            log(f"using character library from {char_path}")
        else:
            character_lib = "NONE"
            log("character.txt missing or empty; using 'NONE'")
    else:
        character_lib = "NONE"

    log(f"story        = {story}")
    log(f"model        = {args.model}")
    log(f"batch size   = {args.batch}")
    log(f"force        = {args.force}")

    client = make_client()

    # ---- Stage A ----
    if config_path.is_file() and config_path.stat().st_size > 0 and not args.force:
        log(f"Stage A: skipped ({config_path} already populated; pass FORCE=1 to redo)")
        config_block = read(config_path).strip()
    else:
        config_block = run_stage_a(
            client,
            model=args.model,
            template_path=a_template,
            full_story=full_story,
            character_lib=character_lib,
            genre=args.genre,
            out_path=config_path,
            template_mirror_path=a_mirror,
        ).strip()

    # ---- Stage B ----
    if breakdown_path.is_file() and breakdown_path.stat().st_size > 0 and not args.force:
        log(f"Stage B: skipped ({breakdown_path} already populated; pass FORCE=1 to redo)")
        breakdown = read(breakdown_path).strip()
    else:
        breakdown = run_stage_b(
            client,
            model=args.model,
            template_path=b_template,
            config_block=config_block,
            full_story=full_story,
            character_lib=character_lib,
            out_path=breakdown_path,
            template_mirror_path=b_mirror,
        ).strip()

    # ---- Stage C ----
    if prompt_path.is_file() and prompt_path.stat().st_size > 0 and not args.force:
        sys.exit(
            f"error: {prompt_path} is non-empty. Refusing to overwrite. "
            "Re-run with FORCE=1 to redo Stage C."
        )

    run_stage_c(
        client,
        model=args.model,
        template_path=c_template,
        config_block=config_block,
        breakdown=breakdown,
        character_lib=character_lib,
        batch_size=args.batch,
        out_path=prompt_path,
        template_mirror_path=c_mirror,
    )

    log("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
