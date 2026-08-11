#!/usr/bin/env python3
"""
deepseek_pipeline.py — run Stage A (+ B + batched C) using DeepSeek OpenAI-compatible API.


Non-developer INI defaults (loaded every run):

  • Edit ``crime-section/deepseek.config.example.ini`` directly for model, temps, pipeline step, searches, tokens, …
    Values are merged with ``setdefault`` so Terminal exports and repo ``.env`` still override the same key.
  • Set ``DEEPSEEK_CONFIG_PATH`` to swap in a totally different INI file.
  • Keep API keys in repo-root ``.env`` (never in the INI).
  • Precedence: Terminal export → ``.env`` → INI defaults → argparse built-ins.

Env tuning (truncate / token budget):
  DEEPSEEK_MAX_TOKENS_A/B/C — max completion tokens per call (defaults raised to reduce cut-offs).
  DEEPSEEK_THINKING=0 — if thinking mode steals budget and CONTENT still truncates at length.
  DEEPSEEK_ALLOW_TRUNCATED=1 — **unsafe** keeps partial replies anyway (normally we exit on length).
  DEEPSEEK_API_MAX_RETRIES (INI ``deepseek_connection.api_max_retries``) — backoff retries on transient
    transport errors (HTTP connection resets / read timeouts mid-stream). DEEPSEEK_API_RETRY_BASE_SEC /
    DEEPSEEK_API_RETRY_MAX_SEC tune exponential sleep (defaults 8s base, cap 120s).

TTY progress + dump each completion (Stages A/B/C):

  • ``terminal.show_progress_bar`` / ``--progress-bar`` — coarse **overall % + ASCII bar** plus a short caption
    (what stage/API call is running). Separate from dumping model text.
  • Typical **quiet terminal**: ``show_api_output = false``, ``show_progress_bar = true`` → progress only + logs to files.
  • INI / CLI ``--show-api-output`` / ``--hide-api-output`` — echo model text after completions (large replies clipped unless
    ``DEEPSEEK_TERMINAL_MAX_CHARS=0``).
  • ``--stream-api-output`` — live token streaming (only applies when ``show_api_output`` is on).
  • Stage B can print breakdown in chunks when ``show_api_output`` is on — ``terminal.stage_b_terminal_scenes`` /
    ``--stage-b-terminal-scenes`` (``0`` = single block).

API parity checklist vs typical DeepSeek samples:

  • OpenAI-compatible client + ``https://api.deepseek.com`` — yes.
  • ``messages`` roles ``system`` + ``user`` (spec half + filled input slots half) — yes.
  • ``max_tokens`` — controlled per stage via ``DEEPSEEK_MAX_TOKENS_*`` (defaults 65536; set lower e.g.
    ``16384`` to match minimal snippets exactly).
  • ``temperature`` — sent for ``deepseek-reasoner`` and for non-thinking v4/chat calls; omitted when v4-style
    thinking mode is enabled (upstream ignores temp in that branch).
  • ``extra_body`` — ``thinking: {type: enabled}`` plus ``reasoning_effort`` only for v4-thinking path;
    skipped for standalone ``*-reasoner`` models so we do not duplicate chain-of-thought plumbing.
  • Web search flag — mapped to ``extra_body.search.type`` (default ``web``); set
    ``DEEPSEEK_SEARCH_LEGACY_ENABLE_SEARCH=1`` if you still need deprecated ``enable_search: true``.
  • Model — default CLI/env ``deepseek-v4-pro``; set ``DEEPSEEK_MODEL=deepseek-reasoner`` (or MY_MODEL_NAME
    / ``--model``) to mirror R1-focused snippets.

Compared to helper/auto_pipeline.py (Claude), there is no prompt caching on the DeepSeek path; reasoning,
search, tokens, temperature, and model id are wired as described above.


Convention for --max-step:
  1 → ensure story folder + seeds FULL_STORY.txt from story-to-run/story.txt (no LLM)
  2 → + Stage A LLM → output_config_<slug>.md
  3 → + Stage B LLM → output_story_breakdown_<slug>.md
  4 → + Stage C batched LLM → prompt.txt
     → then derive scene.txt + image-prompts-only.txt + overlay_hints.txt from prompt.txt

  Stage B truncation:
  Set ``token_budget.stage_b_story_segments`` > 1 (or ``--stage-b-story-segments``), e.g. **4–8** on long drafts,
  to split FULL_STORY into balanced slices → one breakdown API call **per slice** → merged file. The resolver
  can **clamp (lower)** slice counts when averaging fewer than ``token_budget.stage_b_min_chars_per_segment``
  chars per FULL_STORY slice while ``stage_b_cap_segments_by_story_length = true``.
  Uses **paragraph-trimmed overlap** plus post-merge scaffolding strip to reduce rewind / bogus LOCKED/END banners.

Placeholders MUST match bifuracted-template/*.md — same constants as auto_pipeline.py.
"""
from __future__ import annotations

import argparse
import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed
import configparser
import dataclasses
import os
import pathlib
import re
import shutil
import sys
import time
from typing import Any, Callable, Mapping, Optional

# ---------- placeholders (mirror auto_pipeline.py) ----------------------------
PH_FULL_STORY_A = "{Paste the full Hindi / Hinglish / English story here.}"
PH_FULL_STORY_B = "{Paste the full Hindi / Hinglish / English story here — same as used in Stage A.}"
PH_GENRE = "{Paste optional genre or tone hint here, or leave blank.}"
PH_CONFIG = "{Paste the STORY CONFIG BLOCK output from Stage A here.}"
PH_BREAKDOWN = "{Paste the LOCKED SCENE BREAKDOWN output from Stage B here.}"
PH_SCENE_RANGE = (
    '{Example: "Scenes 1–10". Specify the scenes to generate IMAGE PROMPT '
    "+ DIGEN MOTION PROMPT for in this call.}"
)

CHAR_LIB_RE = re.compile(
    r"\{Paste (?:the full contents of the locked character library|the same (?:story-specific )?locked character library text)[^}]*\}",
    re.DOTALL,
)

# Line-start Scene N … (Stage B locked breakdown); ignores inline "Reason: Scene 1".
# Also matches letter-suffixed splits (10a, 71B) from ceiling-repair — renumbered later.
STAGE_B_SCENE_HEADING_LINE = re.compile(
    r"(?m)^\s*--- Scene [^\n]+ ---\s*$",
)

# Catches malformed headings missing the "~M" total placeholder, e.g. "--- Scene 143 / ~---"
# (no space before the closing dashes). Long single Stage B completions sometimes drop the
# total near the end of the response; without normalization these lines silently fail to match
# STAGE_B_SCENE_HEADING_LINE and their content gets swallowed into the previous scene's block.
STAGE_B_SCENE_HEADING_MALFORMED_RE = re.compile(
    r"(?m)^(\s*--- Scene\s+\d+[a-zA-Z]?\s*/\s*~)-{2,}\s*$",
)


def normalize_stage_b_headings(text: str) -> str:
    """Repair malformed '~---' (missing total) Stage B headings into '~0 ---' so they are
    recognized as real scene boundaries by STAGE_B_SCENE_HEADING_LINE."""
    return STAGE_B_SCENE_HEADING_MALFORMED_RE.sub(lambda m: f"{m.group(1)}0 ---", text)

PART3_MARKER = "PART 3 — INPUT SLOTS"


def log(msg: str) -> None:
    print(f"[deepseek-pipeline] {msg}", flush=True)


# region agent log
_DEBUG_LOG_PATH = pathlib.Path(
    "/Users/averma/project/research-story-17thmay-automation/.cursor/debug-6fae5e.log"
)


def _debug_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    import json as _json
    import time as _time

    entry = {
        "sessionId": "6fae5e",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(_time.time() * 1000),
    }
    try:
        _DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _DEBUG_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(_json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass
# endregion agent log


@dataclasses.dataclass(frozen=True)
class TerminalUi:
    """TTY behaviour for Stage A/B/C completions (verbosity is independent of file saves)."""

    show_completion_text: bool
    stream_completions_to_stdout: bool
    max_print_chars: int
    stage_b_terminal_scenes_per_batch: int
    show_progress_bar: bool


def minimal_api_terminal(terminal: Optional[TerminalUi]) -> bool:
    """Suppress per-call token chatter when user wants progress-first / quiet completions."""
    return bool(
        terminal
        and terminal.show_progress_bar
        and not terminal.show_completion_text
    )


def emit_pipeline_progress(*, pct: int, caption: str, detail: str = "") -> None:
    """Single-line coarse progress: ``[######---]  37% · caption · detail``."""
    pct = max(0, min(100, int(pct)))
    bar_w = 26
    filled = int(round((pct / 100.0) * bar_w))
    filled = max(0, min(bar_w, filled))
    bar = "[" + "#" * filled + "-" * (bar_w - filled) + "]"
    tail = f" · {detail}" if detail.strip() else ""
    log(f"PROGRESS {bar} {pct:>3}% · {caption}{tail}")


class PipelineProgressTracker:
    """Maps pipeline milestones to approximate overall completion (TTY only)."""

    _C_SEGMENT_LO = 55
    _C_SEGMENT_HI = 99

    def __init__(self, *, max_step: int, terminal: TerminalUi) -> None:
        self.max_step = max_step
        self.enabled = terminal.show_progress_bar
        self._finished = False

    def _emit(self, pct: int, caption: str, detail: str = "") -> None:
        if self.enabled:
            emit_pipeline_progress(pct=pct, caption=caption, detail=detail)

    def llm_phases_prepare(self) -> None:
        self._emit(2, "Pipeline", "opening LLM phases (folders + story synced)")

    # ----- Stage A -----

    def stage_a_waiting_api(self, *, outfile_name: str) -> None:
        self._emit(12, "Stage A", f"calling DeepSeek API · story config → {outfile_name}")

    def stage_a_using_cache(self, *, outfile_name: str) -> None:
        if self.max_step <= 2:
            self._emit(97, "Stage A (skipped)", f"using existing · {outfile_name}")
        elif self.max_step == 3:
            self._emit(45, "Stage A (skipped)", outfile_name)
        else:
            self._emit(30, "Stage A (skipped)", outfile_name)

    def stage_a_finished_write(self, *, outfile_name: str) -> None:
        if self.max_step <= 2:
            self._emit(97, "Stage A complete", f"wrote {outfile_name}")
        elif self.max_step == 3:
            self._emit(45, "Stage A complete", f"wrote {outfile_name}")
        else:
            self._emit(32, "Stage A complete", f"wrote {outfile_name}")

    # ----- Stage B -----

    def stage_b_waiting_api(self, *, outfile_name: str, segment_note: str = "") -> None:
        tail = segment_note.strip()
        detail = f"calling DeepSeek API · scene breakdown → {outfile_name}"
        if tail:
            detail = f"{detail} · {tail}"
        if self.max_step == 4:
            self._emit(36, "Stage B", detail)
        else:
            self._emit(52, "Stage B", detail)

    def stage_b_using_cache(self, *, outfile_name: str) -> None:
        if self.max_step <= 3:
            self._emit(97, "Stage B (skipped)", f"using existing · {outfile_name}")
        else:
            self._emit(52, "Stage B (skipped)", f"using existing · {outfile_name}")

    def stage_b_finished_write(self, *, outfile_name: str) -> None:
        if self.max_step <= 3:
            self._emit(97, "Stage B complete", f"wrote {outfile_name}")
        else:
            self._emit(52, "Stage B complete", f"wrote {outfile_name}")

    # ----- Stage C -----

    def stage_c_prepare(self, *, total_scenes: int, batch_size: int, batches: int) -> None:
        self._emit(
            53,
            "Stage C prepare",
            f"{total_scenes} scenes · {batches} API batch(es) × up to ~{batch_size} scenes",
        )

    def stage_c_batch_waiting_api(
        self,
        *,
        batch_idx: int,
        batches: int,
        cur_scene: int,
        total_scenes: int,
        range_label: str,
    ) -> None:
        if batches <= 0:
            pct = self._C_SEGMENT_LO
        else:
            pct = self._C_SEGMENT_LO + int(
                (self._C_SEGMENT_HI - self._C_SEGMENT_LO) * (batch_idx - 1) / batches
            )
        self._emit(
            max(self._C_SEGMENT_LO, min(pct, self._C_SEGMENT_HI - 1)),
            f"Stage C batch {batch_idx}/{batches}",
            f"sending DeepSeek · {range_label} (saved through {max(0, cur_scene - 1)}/{total_scenes})",
        )

    def stage_c_batch_appended(
        self,
        *,
        batch_idx: int,
        batches: int,
        scenes_saved_through: int,
        total_scenes: int,
        chars_written: int,
        extra_note: str = "",
    ) -> None:
        if batches <= 0:
            pct = self._C_SEGMENT_HI
        else:
            pct = self._C_SEGMENT_LO + int(
                (self._C_SEGMENT_HI - self._C_SEGMENT_LO) * batch_idx / batches
            )
        tail = extra_note.strip()
        suffix = f" · {tail}" if tail else ""
        self._emit(
            max(self._C_SEGMENT_LO + 1, min(pct, self._C_SEGMENT_HI)),
            f"Stage C batch {batch_idx}/{batches} done",
            f"saved scenes through {min(scenes_saved_through, total_scenes)}/{total_scenes} · appended ≈{chars_written} chars{suffix}",
        )

    def pipeline_complete(self, *, hint: str = "all stages finished — outputs on disk") -> None:
        if not self.enabled or self._finished:
            return
        self._finished = True
        emit_pipeline_progress(pct=100, caption="Complete", detail=hint)


def getenv_int(primary: str, *, default: int) -> int:
    raw = os.environ.get(primary)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(str(raw).strip())
    except ValueError:
        sys.exit(f"error: {primary} expects an integer, got {raw!r}")


def _asciibar(fraction: float, width: int = 28) -> str:
    f = max(0.0, min(1.0, fraction))
    filled = int(round(f * width))
    filled = max(0, min(width, filled))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def log_stage_c_progress(
    *,
    scenes_done_through: int,
    total_scenes: int,
    batch_idx: int,
    estimated_batches: int,
    cur_scene: int,
    batch_end_scene: int,
    phase: str,
) -> None:
    """One-line ASCII progress after each Stage C milestone (cheap; always emitted)."""
    if total_scenes <= 0:
        return
    frac = scenes_done_through / total_scenes
    bar = _asciibar(frac)
    rng = f"queued {cur_scene}–{batch_end_scene}"
    log(
        f"[Stage C] {bar} scenes saved through "
        f"{scenes_done_through}/{total_scenes} • batch {batch_idx}/{estimated_batches} • {rng} • {phase}"
    )


def _truncate_for_terminal(text: str, max_print_chars: int, *, artifact_label: str) -> tuple[str, str]:
    """Return (visible_text, footer_note). ``max_print_chars`` 0 disables shortening."""
    if max_print_chars <= 0 or len(text) <= max_print_chars:
        return text, ""
    head = max_print_chars // 2
    tail = max(max_print_chars - head - 80, 2000)
    show = (
        text[:head]
        + "\n\n... ─── [terminal truncated middle] ─── "
        "... use output file or set DEEPSEEK_TERMINAL_MAX_CHARS=0 ─── ...\n\n"
        + text[-tail:]
    )
    note = (
        f"\n[Terminal preview shortened (total reply {len(text)} chars); "
        f"full file → {artifact_label}]\n"
    )
    return show, note


def print_model_completion_block(
    *,
    label: str,
    text: str,
    artifact_hint: Optional[pathlib.Path],
    max_print_chars: int,
) -> None:
    sep = "=" * 72
    hdr = f"\n{sep}\n[deepseek-pipeline] MODEL OUTPUT — {label}\n{sep}\n"
    print(hdr, flush=True)
    where = str(artifact_hint) if artifact_hint else "(output path)"
    show, end_note = _truncate_for_terminal(text, max_print_chars, artifact_label=where)
    print(show, flush=True)
    if end_note:
        print(end_note, flush=True)
    print(sep + "\n", flush=True)


def split_stage_b_by_scene_headings(text: str) -> Optional[tuple[str, list[str]]]:
    """
    Split a Stage B breakdown into (preamble_before_first_scene, scene_sections).
    Scene sections start at line-start ``Scene N`` (optional ``###`` / ``---`` prefix).
    Returns None if no headings found (caller prints the whole reply normally).
    """
    text = normalize_stage_b_headings(text)
    ms = list(STAGE_B_SCENE_HEADING_LINE.finditer(text))
    if not ms:
        return None
    preamble = text[: ms[0].start()]
    scenes: list[str] = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        scenes.append(text[m.start() : end])
    return preamble, scenes


def _scene_num_from_heading_line(line: str) -> Optional[int]:
    m = re.search(r"Scene\s+(\d+)\b", line)
    return int(m.group(1)) if m else None


def print_stage_b_terminal_in_scene_batches(
    *,
    label: str,
    text: str,
    artifact_hint: Optional[pathlib.Path],
    max_print_chars: int,
    scenes_per_batch: int,
) -> None:
    """TTY-only: print Scene 1..N in sequential chunks (disk write is already the full text)."""
    if scenes_per_batch <= 0:
        print_model_completion_block(
            label=label,
            text=text,
            artifact_hint=artifact_hint,
            max_print_chars=max_print_chars,
        )
        return
    parsed = split_stage_b_by_scene_headings(text)
    if parsed is None:
        log(
            "[Stage B] could not find line-start Scene N headings — "
            "printing full reply as a single terminal block (still saved to file)."
        )
        print_model_completion_block(
            label=label,
            text=text,
            artifact_hint=artifact_hint,
            max_print_chars=max_print_chars,
        )
        return
    preamble, scenes = parsed
    if not scenes:
        print_model_completion_block(
            label=label,
            text=text,
            artifact_hint=artifact_hint,
            max_print_chars=max_print_chars,
        )
        return

    where = str(artifact_hint) if artifact_hint else "(output path)"
    sep = "=" * 72
    n_batches = max(1, (len(scenes) + scenes_per_batch - 1) // scenes_per_batch)
    print(f"\n{sep}\n[deepseek-pipeline] MODEL OUTPUT — {label}\n{sep}\n", flush=True)
    print(
        f"[Stage B] Terminal: {len(scenes)} scene block(s), up to {scenes_per_batch} per print chunk "
        f"({n_batches} chunk(s)). Full text → {where}\n",
        flush=True,
    )

    if preamble.strip():
        log("[Stage B] terminal chunk 0 — preamble (before first Scene line)")
        show, note = _truncate_for_terminal(
            preamble.rstrip() + "\n", max_print_chars, artifact_label=where
        )
        print(show, flush=True)
        if note:
            print(note, flush=True)
        print("-" * 72 + "\n", flush=True)

    for i in range(0, len(scenes), scenes_per_batch):
        batch = scenes[i : i + scenes_per_batch]
        part = i // scenes_per_batch + 1
        merged = "\n\n".join(s.rstrip() for s in batch)
        first_ln = batch[0].split("\n", 1)[0]
        last_ln = batch[-1].split("\n", 1)[0]
        ns = _scene_num_from_heading_line(first_ln)
        ne = _scene_num_from_heading_line(last_ln)
        rng = f"Scenes {ns}–{ne}" if ns is not None and ne is not None else f"blocks {part}"
        log(f"[Stage B] terminal chunk {part}/{n_batches} ({rng}, {len(batch)} scene block(s))")
        show, note = _truncate_for_terminal(merged, max_print_chars, artifact_label=where)
        print(show, flush=True)
        if note:
            print(note, flush=True)
        print("-" * 72 + "\n", flush=True)

    print(sep + "\n", flush=True)


def read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: pathlib.Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")


def split_at_part3(template_text: str) -> tuple[str, str]:
    idx = template_text.find(PART3_MARKER)
    if idx < 0:
        sys.exit(f"error: '{PART3_MARKER}' not found in template")
    start = template_text.rfind("\n", 0, idx)
    if start < 0:
        start = idx
    sep_above = template_text.rfind("=" * 40, 0, start)
    if sep_above >= 0:
        line_start = template_text.rfind("\n", 0, sep_above)
        cut = line_start + 1 if line_start >= 0 else sep_above
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
    parsed = split_stage_b_by_scene_headings(stage_b_output)
    if parsed:
        return len(parsed[1])
    nums = [int(m.group(1)) for m in re.finditer(r"\bScene\s+(\d+)\b", stage_b_output)]
    return max(nums) if nums else 0


def renumber_stage_b_scenes(breakdown: str) -> str:
    """
    Renumber all Stage B scene blocks sequentially (1..N).

    Ceiling-repair sometimes emits letter suffixes (Scene 10a, Scene 10b) which
    collide when parsers read only the leading digits — Stage C then cannot find
    a clean Scene 10 block.
    """
    parsed = split_stage_b_by_scene_headings(breakdown)
    if not parsed:
        return breakdown
    preamble, scenes = parsed
    if not scenes:
        return breakdown

    renumbered: list[str] = []
    letter_suffixes = 0
    for i, block in enumerate(scenes, 1):
        lines = block.strip().splitlines()
        if not lines:
            continue
        first = lines[0]
        if re.search(r"Scene\s+\d+[a-zA-Z]", first):
            letter_suffixes += 1
        approx_m = re.search(r"/\s*~(\d+)", first)
        timing = approx_m.group(1) if approx_m else "?"
        lines[0] = f"--- Scene {i} / ~{timing} ---"
        renumbered.append("\n".join(lines))

    if letter_suffixes:
        log(
            f"Stage B: renumbered {letter_suffixes} letter-suffixed scene(s) "
            f"(e.g. 10a/10b) → sequential integers 1–{len(renumbered)}"
        )
    elif len(renumbered) != len(scenes):
        log(f"Stage B: renumbered {len(renumbered)} scene blocks sequentially (1–{len(renumbered)})")

    body = "\n\n".join(renumbered) + "\n"
    if preamble.strip():
        return preamble.rstrip() + "\n\n" + body
    return body


_STAGE_C_DASHES = r"[\-\u2013\u2014]"  # -, – (en), — (em)

# Canonical Stage C heading (what the template asks for). Some model replies drift slightly
# (missing trailing dashes, different dash glyphs, extra whitespace). We normalize those
# variants before splitting, so we don't falsely treat a scene as "missing".
STAGE_C_PROMPT_HEADING_RE = re.compile(
    rf"^{_STAGE_C_DASHES}{{3,}}\s*Scene\s+(\d+)\s*/\s*~?(\d+|\?)\s*{_STAGE_C_DASHES}{{0,}}\s*$",
    re.MULTILINE | re.IGNORECASE,
)

STAGE_C_PROMPT_HEADING_LOOSE_RE = re.compile(
    rf"^\s*{_STAGE_C_DASHES}{{0,}}\s*Scene\s+(\d+)\s*/\s*~?(\d+|\?)\s*{_STAGE_C_DASHES}{{0,}}\s*(?:#.*)?$",
    re.MULTILINE | re.IGNORECASE,
)


def normalize_stage_c_headings(text: str) -> str:
    """
    Rewrite loose heading variants into a canonical form:
      --- Scene N / ~M ---
    This makes scene splitting resilient to minor model formatting drift.
    """

    def repl(m: re.Match[str]) -> str:
        n = m.group(1)
        total = m.group(2)
        if total == "?":
            total = "0"
        return f"--- Scene {n} / ~{total} ---"

    return STAGE_C_PROMPT_HEADING_LOOSE_RE.sub(repl, text)


def parse_stage_c_scene_numbers(text: str) -> list[int]:
    """Scene numbers present in Stage C prompt output (``--- Scene N / ~M ---`` headings)."""
    norm = normalize_stage_c_headings(text)
    return sorted({int(m.group(1)) for m in STAGE_C_PROMPT_HEADING_RE.finditer(norm)})


def split_stage_c_prompt_blocks(text: str) -> dict[int, str]:
    """Split a Stage C prompt file into per-scene blocks keyed by scene number."""
    text = normalize_stage_c_headings(text)
    matches = list(STAGE_C_PROMPT_HEADING_RE.finditer(text))
    if not matches:
        return {}
    blocks: dict[int, str] = {}
    for i, m in enumerate(matches):
        n = int(m.group(1))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks[n] = text[start:end].rstrip() + "\n\n"
    return blocks


def merge_stage_c_prompt_blocks(blocks: Mapping[int, str], total: int) -> str:
    missing = [n for n in range(1, total + 1) if n not in blocks]
    if missing:
        preview = ", ".join(str(x) for x in missing[:24])
        tail = "..." if len(missing) > 24 else ""
        sys.exit(f"error: prompt still missing scene(s): {preview}{tail}")
    return "".join(blocks[n] for n in range(1, total + 1))


def run_prompt_derivative_export(
    prompt_path: pathlib.Path,
    *,
    client_kwargs: Mapping[str, Any] | None = None,
    force: bool = False,
) -> None:
    """Default Step 4 post-pass: scene.txt, image-prompts-only.txt, overlay_hints.txt."""
    if not prompt_path.is_file() or prompt_path.stat().st_size == 0:
        log(f"WARN: derivative export skipped — {prompt_path.name} missing or empty")
        return
    try:
        from export_prompt_derivatives import export_prompt_derivatives

        export_prompt_derivatives(
            prompt_path,
            split_blocks=split_stage_c_prompt_blocks,
            client_kwargs=client_kwargs,
            call_llm=call_deepseek,
            force=force,
            log=log,
        )
    except (FileNotFoundError, ValueError) as exc:
        log(f"WARN: derivative export skipped — {exc}")


def find_missing_prompt_scenes(prompt_text: str, total: int) -> list[int]:
    have = set(parse_stage_c_scene_numbers(prompt_text))
    return [n for n in range(1, total + 1) if n not in have]


def _missing_scene_ranges(missing: list[int]) -> list[tuple[int, int]]:
    if not missing:
        return []
    ranges: list[tuple[int, int]] = []
    start = prev = missing[0]
    for n in missing[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append((start, prev))
        start = prev = n
    ranges.append((start, prev))
    return ranges


def _stage_c_min_chars_for_range(start: int, end: int) -> int:
    per_scene = max(400, getenv_int("STAGE_C_MIN_CHARS_PER_SCENE", default=1200))
    return (end - start + 1) * per_scene


def _split_even_chars(text: str, n_parts: int) -> list[str]:
    """Fallback splitter when paragraphs are fewer than requested parts."""
    n_parts = max(1, n_parts)
    if n_parts <= 1:
        return [text.strip()]
    L = len(text)
    if L == 0:
        return [""]
    step = max(1, L // n_parts)
    out: list[str] = []
    start = 0
    for i in range(n_parts):
        if i == n_parts - 1:
            out.append(text[start:].strip())
            break
        cut = min(L, start + step)
        window_hi = min(L, cut + step // 3)
        nl = text.rfind("\n", max(start, cut - step // 2), window_hi)
        if nl > start:
            cut = nl + 1
        out.append(text[start:cut].strip())
        start = cut
    merged = [x for x in out if x]
    return merged if merged else [text.strip()]


def _tail_overlap_at_paragraph(prev: str, overlap_chars: int) -> str:
    """Use the tail of *prev* for cross-slice continuity, starting at last paragraph boundary when possible."""
    if overlap_chars <= 0 or not prev:
        return ""
    chunk = prev[-overlap_chars:] if len(prev) > overlap_chars else prev
    nl = chunk.rfind("\n\n")
    # Keep overlap mostly inside paragraphs when we can anchor on a cleaner break near the slice join.
    if nl >= max(24, overlap_chars // 4):
        chunk = chunk[nl + 2 :]
    return chunk.strip()


def strip_stage_b_slice_scaffolding(blob: str) -> tuple[str, int]:
    """
    Models often invent mid-file scaffolding (section rails, fake ``END OF`` markers).
    Strip these so merges stay one continuous LOCKED SCENE BREAKDOWN stream.
    """
    if not blob or not blob.strip():
        return blob, 0
    sep_line = re.compile(r"^[ \t]*(=){8,}[ \t]*$")

    def is_banner_middle(line: str) -> bool:
        s = line.strip()
        return s.startswith("LOCKED SCENE BREAKDOWN") or ("END OF LOCKED SCENE BREAKDOWN" in s)

    lines = blob.splitlines()
    dropped = 0
    out_lines: list[str] = []
    i = 0
    while i < len(lines):
        if sep_line.match(lines[i]) and i + 2 < len(lines) and sep_line.match(lines[i + 2]):
            if is_banner_middle(lines[i + 1]):
                dropped += 1
                i += 3
                while i < len(lines) and lines[i].strip() == "":
                    i += 1
                continue
        # Single-line orphans that only repeat section titles (no ruler sandwich)
        s = lines[i].strip()
        if s.startswith("LOCKED SCENE BREAKDOWN") or s == "END OF LOCKED SCENE BREAKDOWN":
            i += 1
            continue
        if sep_line.match(lines[i]):
            i += 1
            dropped += 1
            continue
        out_lines.append(lines[i])
        i += 1
    merged = "\n".join(out_lines).strip()
    merged = re.sub(r"\n{3,}", "\n\n", merged)
    return merged, dropped


def split_story_into_balanced_segments(text: str, n_parts: int) -> list[str]:
    """
    Split episode text into ``n_parts`` balanced slices at paragraph boundaries when possible.
    Used for multi-call Stage B (each slice gets its own DeepSeek completion).
    """
    text = (text or "").strip()
    n_parts = max(1, int(n_parts))
    if n_parts <= 1:
        return [text]
    paras = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    if not paras:
        return _split_even_chars(text, n_parts)
    if len(paras) < n_parts:
        return _split_even_chars("\n\n".join(paras), n_parts)

    total_chars = sum(len(p) for p in paras)
    target = total_chars / n_parts
    buckets: list[list[str]] = [[] for _ in range(n_parts)]
    sizes = [0] * n_parts
    bi = 0
    for p in paras:
        buckets[bi].append(p)
        sizes[bi] += len(p) + 2
        if bi < n_parts - 1 and sizes[bi] >= target:
            bi += 1
    segments = ["\n\n".join(b).strip() for b in buckets]
    return [s for s in segments if s] or [text]


def resolve_stage_b_segment_count(*, full_story: str, requested: int) -> int:
    """
    How many FULL_STORY slices Stage B should use.

    • ``requested > 0``: fixed slice count (clamped to a hard ceiling).
    • ``requested <= 0``: derive from ``len(full_story)`` and ``STAGE_B_AUTO_TARGET_CHARS`` (characters per slice).
    """
    hard = max(1, getenv_int("STAGE_B_SEGMENT_HARD_CAP", default=24))
    story = (full_story or "").strip()
    L = len(story)

    if requested > 0:
        n_before = min(max(1, int(requested)), hard)
        if n_before <= 1:
            return 1
        n_fin = _clamp_stage_b_slices_by_story_chars(n_before, L)
        if n_fin < n_before:
            log(
                f"Stage B segments: story-length clamp {n_before} → {n_fin} slices · "
                f"story≈{L} chars · set stage_b_cap_segments_by_story_length = false "
                "or tweak stage_b_min_chars_per_segment to override."
            )
        log(f"Stage B segments: configured {requested}, hard_ceiling={hard}, **using {n_fin} slice(s)**")
        return max(1, n_fin)

    per = getenv_int("STAGE_B_AUTO_TARGET_CHARS", default=1300)
    if per <= 0 or L <= 0:
        log("Stage B segments: auto mode but invalid target_chars or empty story → 1 slice.")
        return 1
    raw = max(1, (L + per - 1) // per)
    n_before = min(raw, hard)
    if n_before <= 1:
        return 1
    n_fin = _clamp_stage_b_slices_by_story_chars(n_before, L)
    log(
        f"Stage B segments: auto (~{per} chars/slice · raw={raw} · hard_ceiling={hard} · story≈{L} chars)"
        + (f" · clamped {n_before}→{n_fin}" if n_fin < n_before else "")
        + f" · **final {n_fin} slice(s)**"
    )
    return max(1, n_fin)


def _clamp_stage_b_slices_by_story_chars(n_seg: int, story_chars: int) -> int:
    """
    Thin stories + many slices → boundary confusion and rewind / duplication.
    Clamp when ``STAGE_B_CAP_SEGMENTS_BY_STORY_LENGTH`` is true (default yes).
    """
    if (
        n_seg <= 1
        or story_chars <= 0
        or not getenv_bool("STAGE_B_CAP_SEGMENTS_BY_STORY_LENGTH", default=True)
    ):
        return n_seg
    min_chars = getenv_int("STAGE_B_MIN_CHARS_PER_SEGMENT", default=2600)
    if min_chars <= 0:
        return n_seg
    allowed = max(1, story_chars // min_chars)
    if n_seg <= allowed:
        return n_seg
    return max(1, allowed)


def apply_story_segment_overlap(segments: list[str], overlap_chars: int) -> list[str]:
    """Prefix each slice after the first with a tail from the previous slice for continuity."""
    if overlap_chars <= 0 or len(segments) <= 1:
        return segments
    overlap_label = (
        "--- [CONTEXT OVERLAP — recap only · already covered — DO NOT invent new Scene entries "
        "for these sentences · never rewind or reorganize earlier beats] ---"
    )
    new_label = (
        "--- [AUTHORITATIVE CONTINUATION — EVERY new Scene must map ONLY to this body — "
        "strict chronological episode order · Hindi line quotations must match VERBATIM] ---"
    )
    out = [segments[0]]
    for i in range(1, len(segments)):
        prev = segments[i - 1]
        ov = _tail_overlap_at_paragraph(prev, overlap_chars)
        cur = segments[i].lstrip()
        out.append(f"{ov}\n\n{overlap_label}\n\n{new_label}\n\n{cur}".strip())
    return out


def stage_b_pipeline_split_banner(seg_idx: int, seg_total: int, scenes_locked_through: int) -> str:
    """Instructions appended after each story excerpt when Stage B runs in multi-call mode."""
    lines = [
        "=" * 72,
        "PIPELINE — STORY SPLIT MODE (automatic)",
        "=" * 72,
        f"You receive excerpt {seg_idx + 1} of {seg_total} sequential slices of ONE episode.",
        "The STORY CONFIG BLOCK (above slot) applies to every slice.",
        "",
        "RULES:",
        "- Do NOT paste template headers inside the breakdown (no extra “LOCKED SCENE BREAKDOWN” rails, ",
        '  no “END OF …” markers, no excerpt titles). Emit scene blocks only (“--- Scene N … ---”).',
        "- CONTEXT OVERLAP (if shown) duplicates prior script beats for memory only.",
        "- First new scene after CONTEXT OVERLAP must pick up the storyline immediately AFTER that overlap;",
        '  never jump backward earlier in the episode.',
        "",
    ]
    if scenes_locked_through <= 0:
        lines.append(
            "Emit ONLY new LOCKED SCENE BREAKDOWN entries for beats whose PRIMARY narrative appears in THIS excerpt."
        )
        lines.append("Number scenes starting at Scene 1.")
    else:
        lines.append(
            f"Earlier slices already locked scenes through Scene {scenes_locked_through}. "
            f"Continue numbering strictly from Scene {scenes_locked_through + 1}."
        )
        lines.append(
            "Emit ONLY NEW scenes for beats in THIS excerpt — never repeat or rewrite scenes from earlier slices."
        )
        lines.append(
            f"Never re-number downward; Hindi lines under Scene {scenes_locked_through + 1}+ must come from "
            "the NEW-STORY BODY after overlap markers."
        )
    lines.extend(
        [
            "",
            "HARD CEILING — pipeline enforced on every slice:",
            "- Every Hindi line MUST be ≤25 spoken words AND ≤100 visible characters.",
            "- If a line exceeds either limit, split into multiple Scene blocks.",
            "- Split order: । ? ! close-quote → em-dash (—) → clause markers → comma (last resort).",
            '- NEVER write "Length exception accepted". No exception path exists.',
            "",
            "Output ONLY the LOCKED SCENE BREAKDOWN body using the normal Stage B format from this template.",
            "=" * 72,
        ]
    )
    return "\n".join(lines)


STAGE_B_HARD_CEILING_BANNER = """
================================================================================
PIPELINE HARD CEILING — NON-NEGOTIABLE
================================================================================
Every Hindi line MUST be ≤25 spoken words AND ≤100 visible characters.
If a line exceeds either limit, split it into multiple Scene blocks.
Split order: । ? ! close-quote → em-dash (—) → clause markers (कि, जब, लेकिन, और) → comma (last resort).
Preserve exact source Hindi wording — do not paraphrase.
NEVER write "Length exception accepted". There is no exception path.
================================================================================
""".strip()

STAGE_B_MAX_HINDI_WORDS = 25
STAGE_B_MAX_HINDI_CHARS = 100


def _hindi_line_metrics(line: str) -> tuple[int, int]:
    text = line.strip()
    return len(text.split()), len(text)


def _extract_hindi_from_scene_block(block: str) -> str:
    inline = re.search(r"(?m)^Hindi line:\s+(\S.+)$", block)
    if inline:
        return inline.group(1).strip()
    m = re.search(r"(?m)^Hindi line:\s*\n(.+?)(?=\n\n)", block, re.DOTALL)
    return m.group(1).strip() if m else ""


def find_stage_b_hindi_violations(breakdown: str) -> list[tuple[int, str, int, int]]:
    """Return (scene_num, hindi_line, word_count, char_count) for lines above the hard ceiling."""
    parsed = split_stage_b_by_scene_headings(breakdown)
    if not parsed:
        return []
    _, scenes = parsed
    violations: list[tuple[int, str, int, int]] = []
    for block in scenes:
        first_line = block.strip().splitlines()[0] if block.strip() else ""
        scene_num = _scene_num_from_heading_line(first_line)
        if scene_num is None:
            continue
        hindi = _extract_hindi_from_scene_block(block)
        if not hindi:
            continue
        words, chars = _hindi_line_metrics(hindi)
        if words > STAGE_B_MAX_HINDI_WORDS or chars > STAGE_B_MAX_HINDI_CHARS:
            violations.append((scene_num, hindi, words, chars))
    return violations


def repair_stage_b_hindi_ceiling(
    breakdown: str,
    *,
    client_kwargs: Mapping[str, Any],
    terminal: Optional[TerminalUi] = None,
    max_tokens: int,
) -> str:
    """
    If any Hindi line exceeds the hard ceiling, ask DeepSeek to return a corrected
    full breakdown with those lines split into shorter scenes.
    """
    violations = find_stage_b_hindi_violations(breakdown)
    if not violations:
        return breakdown

    summary = "\n".join(
        f"- Scene {n}: {wc} words, {cc} chars"
        for n, _hindi, wc, cc in violations
    )
    log(
        f"Stage B: {len(violations)} Hindi line(s) exceed hard ceiling "
        f"({STAGE_B_MAX_HINDI_WORDS} words / {STAGE_B_MAX_HINDI_CHARS} chars) — repair pass"
    )

    system_prompt = (
        "You fix Stage B LOCKED SCENE BREAKDOWN output. "
        "Split only Hindi lines that violate the hard ceiling; keep all other scenes unchanged."
    )
    user_prompt = f"""{STAGE_B_HARD_CEILING_BANNER}

These scenes violate the hard ceiling:
{summary}

Return the COMPLETE corrected LOCKED SCENE BREAKDOWN with ALL scenes.
Split each violating Hindi line into multiple Scene blocks until every Hindi line is
≤{STAGE_B_MAX_HINDI_WORDS} words AND ≤{STAGE_B_MAX_HINDI_CHARS} characters.
Preserve exact source Hindi wording. Duplicate metadata for each new scene block.
Renumber ALL scenes with plain integers only (Scene 1, Scene 2, …) — NEVER use
letter suffixes such as Scene 10a or Scene 10b.
Do NOT write "Length exception accepted".

ORIGINAL BREAKDOWN:
{breakdown.strip()}
"""

    text, finish = call_deepseek(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        label="stage-b-ceiling-repair",
        terminal=terminal,
        **client_kwargs,
    )
    abort_if_truncated(finish, "stage-b-ceiling-repair", "DEEPSEEK_MAX_TOKENS_B")
    repaired, _junk = strip_stage_b_slice_scaffolding(text.strip())
    repaired = repaired.strip()
    if parse_scene_count(repaired) <= 0:
        log("WARN: Stage B ceiling repair returned no scenes — keeping original breakdown")
        return breakdown

    remaining = find_stage_b_hindi_violations(repaired)
    if remaining:
        log(
            f"WARN: Stage B ceiling repair still has {len(remaining)} long Hindi line(s) "
            f"— using repaired output anyway"
        )
    else:
        log("Stage B: ceiling repair succeeded — all Hindi lines within limits")
    return repaired + "\n"


def parse_next_range_start(text: str) -> Optional[int]:
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


def load_repo_dotenv(repo_root: pathlib.Path) -> None:
    """Load repo-root .env without printing secrets."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = repo_root / ".env"
    if env_path.is_file():
        load_dotenv(env_path)


def getenv_nonempty(var: str) -> Optional[str]:
    r = os.environ.get(var)
    if r is None:
        return None
    stripped = str(r).strip()
    return stripped if stripped else None


def getenv_bool(primary: str, *aliases: str, default: bool = False) -> bool:
    for key in (primary,) + aliases:
        raw = os.environ.get(key)
        if raw is None:
            continue
        s = str(raw).strip()
        if s == "":
            continue
        if s.lower() in ("1", "true", "yes", "on"):
            return True
        if s.lower() in ("0", "false", "no", "off"):
            return False
        sys.exit(f"error: {key} expects true/false/1/0, got {raw!r}")
    return default


def bootstrap_deepseek_ini(path: pathlib.Path) -> bool:
    """
    Copy INI knobs into ``os.environ`` using ``setdefault`` only —
    precedence: exported shell vars & ``.env`` win over missing keys from INI.

    Sections mirror ``crime-section/deepseek.config.example.ini``.
    """
    path = path.expanduser().resolve()
    if not path.is_file():
        return False
    cp = configparser.ConfigParser(interpolation=None, comment_prefixes=("#", ";"))
    cp.optionxform = str  # preserve option spelling as authored
    read = cp.read(path, encoding="utf-8")
    if not read:
        sys.exit(f"error: could not parse INI configuration {path}")

    def trimmed(section: str, option: str) -> Optional[str]:
        if section not in cp or not cp.has_option(section, option):
            return None
        txt = cp.get(section, option, fallback="").strip()
        return txt if txt else None

    def set_env(key: str, value: Optional[str]) -> None:
        if value is None:
            return
        os.environ.setdefault(key, value)

    def bool_env(key: str, section: str, option: str) -> None:
        raw = trimmed(section, option)
        if raw is None:
            return
        lv = raw.lower()
        if lv in ("1", "true", "yes", "on"):
            os.environ.setdefault(key, "1")
        elif lv in ("0", "false", "no", "off"):
            os.environ.setdefault(key, "0")
        else:
            sys.exit(f"error: [{section}] {option} must be yes/no/true/false/1/0 ({path})")

    def int_env(key: str, section: str, option: str) -> None:
        raw = trimmed(section, option)
        if raw is None:
            return
        try:
            n = int(raw)
        except ValueError:
            sys.exit(f"error: [{section}] {option} must be an integer ({path})")
        os.environ.setdefault(key, str(n))

    set_env("PIPELINE_STORY", trimmed("pipeline", "folder_name"))
    step_raw = trimmed("pipeline", "max_step")
    if step_raw is not None:
        try:
            st = int(step_raw)
            if st not in (1, 2, 3, 4):
                sys.exit(f"pipeline.max_step must be 1–4 in {path}")
        except ValueError:
            sys.exit(f"pipeline.max_step must be a whole number ({path})")
        os.environ.setdefault("DEEPSEEK_MAX_STEP", str(st))
    bool_env("FORCE", "pipeline", "force")
    bool_env("DEEPSEEK_RECREATE_STORY", "pipeline", "recreate_story_folder")
    bool_env("DEEPSEEK_USE_CHARACTER_LIB", "pipeline", "use_character_library")
    set_env("DEEPSEEK_STORY_FILE", trimmed("pipeline", "story_txt_path"))

    set_env("DEEPSEEK_BASE_URL", trimmed("deepseek_connection", "base_url"))
    set_env("DEEPSEEK_MODEL", trimmed("deepseek_connection", "model"))
    int_env("DEEPSEEK_API_MAX_RETRIES", "deepseek_connection", "api_max_retries")

    temp = trimmed("temperature", "value")
    set_env("DEEPSEEK_TEMPERATURE", temp)

    bool_env("DEEPSEEK_THINKING", "thinking", "enabled")
    set_env("DEEPSEEK_REASONING_EFFORT", trimmed("thinking", "reasoning_effort"))

    int_env("DEEPSEEK_MAX_TOKENS_A", "token_budget", "max_tokens_stage_a")
    int_env("DEEPSEEK_MAX_TOKENS_B", "token_budget", "max_tokens_stage_b")
    int_env("DEEPSEEK_MAX_TOKENS_C", "token_budget", "max_tokens_stage_c")
    int_env("STAGE_C_BATCH", "token_budget", "scene_batch")
    int_env("STAGE_C_BATCH_RETRIES", "token_budget", "stage_c_batch_retries")
    int_env("STAGE_C_MIN_CHARS_PER_SCENE", "token_budget", "stage_c_min_chars_per_scene")
    int_env("STAGE_B_STORY_SEGMENTS", "token_budget", "stage_b_story_segments")
    int_env("STAGE_B_AUTO_TARGET_CHARS", "token_budget", "stage_b_auto_target_chars")
    int_env("STAGE_B_SEGMENT_HARD_CAP", "token_budget", "stage_b_segment_hard_cap")
    int_env("STAGE_B_SEGMENT_OVERLAP_CHARS", "token_budget", "stage_b_segment_overlap_chars")
    int_env("STAGE_B_MIN_CHARS_PER_SEGMENT", "token_budget", "stage_b_min_chars_per_segment")
    bool_env("STAGE_B_CAP_SEGMENTS_BY_STORY_LENGTH", "token_budget", "stage_b_cap_segments_by_story_length")
    int_env("STAGE_B_PARALLEL_CALLS", "token_budget", "stage_b_parallel_calls")
    int_env("STAGE_C_PARALLEL_BATCHES", "token_budget", "stage_c_parallel_batches")

    set_env("DEEPSEEK_GENRE", trimmed("genre_hint", "mood_hint"))

    bool_env("DEEPSEEK_ENABLE_SEARCH", "smart_search", "internet_enabled")
    search_kind = trimmed("smart_search", "internet_search_kind")
    if search_kind is not None:
        set_env("DEEPSEEK_SEARCH_TYPE", search_kind)
    legacy = trimmed("smart_search", "internet_search_legacy_dual_flag")
    if legacy is not None:
        lv = legacy.lower()
        flag = lv in ("1", "true", "yes", "on")
        set_env(
            "DEEPSEEK_SEARCH_LEGACY_ENABLE_SEARCH",
            "1" if flag else "0",
        )
    bool_env("DEEPSEEK_ALLOW_TRUNCATED", "safety", "allow_truncated_saves")

    bool_env("DEEPSEEK_SHOW_API_OUTPUT", "terminal", "show_api_output")
    bool_env("DEEPSEEK_STREAM_API_OUTPUT", "terminal", "stream_api_output")
    bool_env("DEEPSEEK_TERMINAL_PROGRESS_BAR", "terminal", "show_progress_bar")
    int_env("DEEPSEEK_TERMINAL_MAX_CHARS", "terminal", "max_print_chars")
    int_env("DEEPSEEK_STAGE_B_TERMINAL_SCENES", "terminal", "stage_b_terminal_scenes")

    log(f"loaded DeepSeek ini defaults from {path}")
    return True


def resolve_api_key() -> str:
    for k in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY"):
        v = os.environ.get(k, "").strip()
        if v:
            return v
    sys.exit(
        "error: set DEEPSEEK_API_KEY (or OPENAI_API_KEY) in the environment "
        "or repo .env loaded via python-dotenv"
    )


def _deepseek_retry_backoff_attempt(attempt_index: int) -> float:
    """Seconds to sleep before attempt_index-th retry (0 = first backoff after first failure)."""
    raw_b = os.environ.get("DEEPSEEK_API_RETRY_BASE_SEC")
    raw_cap = os.environ.get("DEEPSEEK_API_RETRY_MAX_SEC")
    try:
        base = float((raw_b or "").strip() or "8")
    except ValueError:
        base = 8.0
    try:
        cap = float((raw_cap or "").strip() or "120")
    except ValueError:
        cap = 120.0
    return min(cap, base * float(2**attempt_index))


def _retryable_deepseek_transport_err(exc: BaseException) -> bool:
    """Return True when the DeepSeek/OpenAI-compat call should be retried (network blips mid-read)."""
    errno_mod = __import__("errno")
    errno_reset_like = frozenset(
        {
            getattr(errno_mod, "ECONNRESET", -1),
            getattr(errno_mod, "EPIPE", -1),
            getattr(errno_mod, "ETIMEDOUT", -1),
            getattr(errno_mod, "ECONNABORTED", -1),
            54,  # macOS connection reset observed in the wild with httpx
            104,  # Linux ECONNRESET
            10054,  # Windows WSAECONNRESET
        }
    )
    errno_reset_like = {x for x in errno_reset_like if isinstance(x, int) and x >= 0}

    cur: Optional[BaseException] = exc
    while cur is not None:
        if isinstance(cur, TimeoutError):
            return True
        if isinstance(cur, (ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
            return True
        if isinstance(cur, OSError):
            errno_v = getattr(cur, "errno", None)
            if errno_v is not None and errno_v in errno_reset_like:
                return True
        try:
            import httpx as _hx

            if isinstance(
                cur,
                (
                    _hx.ReadError,
                    _hx.ConnectError,
                    _hx.RemoteProtocolError,
                    _hx.ReadTimeout,
                    _hx.WriteTimeout,
                    _hx.ConnectTimeout,
                    _hx.PoolTimeout,
                ),
            ):
                return True
        except ImportError:
            pass
        try:
            import openai as _oa

            ac_err = getattr(_oa, "APIConnectionError", None)
            if ac_err is not None and isinstance(cur, ac_err):
                return True
            ap_to = getattr(_oa, "APITimeoutError", None)
            if ap_to is not None and isinstance(cur, ap_to):
                return True
        except ImportError:
            pass
        cur = cur.__cause__
    return False


def chat_completion_create_with_retries(
    *,
    label: str,
    create_fn: Callable[..., Any],
    kwargs: dict[str, Any],
) -> Any:
    """Call ``chat.completions.create`` with backoff on transient disconnects."""
    max_tries = max(1, getenv_int("DEEPSEEK_API_MAX_RETRIES", default=10))
    for attempt in range(max_tries):
        try:
            return create_fn(**kwargs)
        except Exception as exc:
            retryable = _retryable_deepseek_transport_err(exc)
            terminal_fail = attempt + 1 >= max_tries or not retryable
            if terminal_fail:
                raise
            pause = _deepseek_retry_backoff_attempt(attempt)
            log(
                f"[{label}] transient transport error ({type(exc).__name__}): sleeping {pause:.1f}s "
                f"then retry {attempt + 2}/{max_tries}…"
            )
            time.sleep(pause)


def make_deepseek_extra_body(enable_search: bool, thinking: bool) -> dict[str, Any]:
    eb: dict[str, Any] = {}
    if enable_search:
        # Matches OpenAI-compat samples: extras.search.type (see DeepSeek docs / chat.deepseek parity).
        # Set DEEPSEEK_SEARCH_LEGACY_ENABLE_SEARCH=1 to also send legacy ``enable_search: true``.
        search_type = os.environ.get("DEEPSEEK_SEARCH_TYPE", "web").strip()
        eb["search"] = {"type": search_type}
        if os.environ.get("DEEPSEEK_SEARCH_LEGACY_ENABLE_SEARCH", "").strip().lower() in (
            "1",
            "true",
            "yes",
        ):
            eb["enable_search"] = True
    if thinking:
        eb["thinking"] = {"type": "enabled"}
    return eb


def call_deepseek(
    *,
    api_key: str,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    reasoning_effort: Optional[str],
    enable_search: bool,
    thinking: bool,
    label: str,
    terminal: Optional[TerminalUi] = None,
    artifact_path: Optional[pathlib.Path] = None,
) -> tuple[str, Optional[str]]:
    """Return (assistant_content, finish_reason). finish_reason ``length`` means output hit max_tokens."""
    legacy_reasoner = "reasoner" in (model or "").lower()
    thinking_effective = bool(thinking) and not legacy_reasoner

    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    extra_body = make_deepseek_extra_body(
        enable_search=enable_search,
        thinking=thinking_effective,
    )

    common_kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    create_fn: Callable[..., Any] = client.chat.completions.create

    # Thinking-enabled v4 ignores temperature docs; standalone reasoner + non-thinking chats send it.
    if legacy_reasoner or not thinking_effective:
        common_kwargs["temperature"] = temperature

    re_level = reasoning_effort if thinking_effective else None
    if re_level:
        common_kwargs["reasoning_effort"] = re_level

    if extra_body:
        common_kwargs["extra_body"] = extra_body

    want_stream = bool(
        terminal
        and terminal.show_completion_text
        and terminal.stream_completions_to_stdout
    )

    def log_usage_dt(usage: Any, dt: float) -> None:
        if minimal_api_terminal(terminal):
            return
        if usage is not None:
            try:
                it = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", 0)
                ot = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", 0)
                log(f"[{label}] tokens in≈{it} out≈{ot} {dt:.1f}s")
            except Exception:
                log(f"[{label}] done in {dt:.1f}s")
        else:
            log(f"[{label}] done in {dt:.1f}s")

    def consume_stream(kwargs: dict[str, Any]) -> tuple[str, Optional[str]]:
        """Stream assistant content to stdout."""
        parts: list[str] = []
        finish_s: Optional[str] = None
        usage_seen: Any = None
        t_stream = time.time()
        sep = "=" * 72
        print(
            f"\n{sep}\n[deepseek-pipeline] STREAMING MODEL OUTPUT — {label}\n{sep}\n",
            flush=True,
        )
        stream = create_fn(**kwargs)
        for chunk in stream:
            usage_seen = getattr(chunk, "usage", None) or usage_seen
            if not getattr(chunk, "choices", None):
                continue
            c0 = chunk.choices[0]
            fr = getattr(c0, "finish_reason", None)
            if fr:
                finish_s = fr
            delta = getattr(c0, "delta", None)
            piece = getattr(delta, "content", None) if delta is not None else None
            if piece:
                parts.append(str(piece))
                print(str(piece), end="", flush=True)
        print(flush=True)
        dt_s = time.time() - t_stream
        print(sep + "\n", flush=True)
        log_usage_dt(usage_seen, dt_s)
        merged = "".join(parts).strip()
        return merged, finish_s

    # --- Optional streaming ---
    kw_stream_try = dict(common_kwargs)
    streamed = False
    reply_text = ""
    finish_reason: Optional[str] = None
    if want_stream:
        log(f"[{label}] streaming request to stdout...")
        kw_stream_try["stream"] = True
        stripped_for_stream = False
        stream_transient_attempts = 0
        while True:
            try:
                reply_text, finish_reason = consume_stream(dict(kw_stream_try))
                streamed = True
                break
            except TypeError as e_stream:
                if not stripped_for_stream:
                    stripped_for_stream = True
                    log(f"[{label}] stream+wiring retry ({e_stream})")
                    kw_stream_try.pop("reasoning_effort", None)
                    kw_stream_try.pop("extra_body", None)
                    kw_stream_try.setdefault("temperature", temperature)
                    kw_stream_try["stream"] = True
                    stream_transient_attempts = 0
                    continue
                log(f"[{label}] buffered mode (streaming not supported): {e_stream}")
                streamed = False
                break
            except Exception as transient_stream_err:
                if not _retryable_deepseek_transport_err(transient_stream_err):
                    raise
                retries_stream = max(1, getenv_int("DEEPSEEK_API_MAX_RETRIES", default=10))
                if stream_transient_attempts + 1 >= retries_stream:
                    raise transient_stream_err
                stream_transient_attempts += 1
                nap = _deepseek_retry_backoff_attempt(stream_transient_attempts - 1)
                log(
                    f"[{label}] stream transport ({type(transient_stream_err).__name__}): "
                    f"{stream_transient_attempts}/{retries_stream}, sleep {nap:.1f}s"
                )
                time.sleep(nap)

    # --- Buffered completion (when streaming off or unsupported) ---
    if not streamed:
        t0 = time.time()
        if terminal and terminal.show_completion_text and not want_stream:
            if not minimal_api_terminal(terminal):
                log(f"[{label}] sending request (non-stream)...")
        try:
            resp = chat_completion_create_with_retries(
                label=label, create_fn=create_fn, kwargs=common_kwargs
            )
        except TypeError as e:
            # Older SDK might not accept reasoning_effort/extra_body; strip and retry.
            log(f"WARN: fallback without advanced kwargs ({e})")
            common_kwargs.pop("reasoning_effort", None)
            common_kwargs.pop("extra_body", None)
            common_kwargs.setdefault("temperature", temperature)
            resp = chat_completion_create_with_retries(
                label=label, create_fn=create_fn, kwargs=common_kwargs
            )

        dt = time.time() - t0
        buf_text = ""
        buf_finish: Optional[str] = None
        if resp.choices and len(resp.choices) > 0:
            choice0 = resp.choices[0]
            buf_finish = getattr(choice0, "finish_reason", None)
            msg = choice0.message
            buf_text = getattr(msg, "content", None) or ""
            reasoning = getattr(msg, "reasoning_content", None)
            if reasoning and not minimal_api_terminal(terminal):
                preview = reasoning[:280].replace("\n", " ")
                log(f"[{label}] ... reasoning_preview={preview!s}...")
        usage = getattr(resp, "usage", None)
        log_usage_dt(usage, dt)
        reply_text = (buf_text or "").strip()
        if terminal and terminal.show_completion_text:
            if label == "stage-b" and terminal.stage_b_terminal_scenes_per_batch > 0:
                print_stage_b_terminal_in_scene_batches(
                    label=f"{label} (complete)",
                    text=reply_text,
                    artifact_hint=artifact_path,
                    max_print_chars=terminal.max_print_chars,
                    scenes_per_batch=terminal.stage_b_terminal_scenes_per_batch,
                )
            else:
                print_model_completion_block(
                    label=f"{label} (complete)",
                    text=reply_text,
                    artifact_hint=artifact_path,
                    max_print_chars=terminal.max_print_chars,
                )
        finish_reason = buf_finish

    if finish_reason == "length":
        log(f"[{label}] WARNING: finish_reason=length, output hit max_tokens and may be unusable downstream")

    return reply_text, finish_reason


def abort_if_truncated(finish_reason: Optional[str], label: str, token_env_var: str) -> None:
    """Stop pipeline if completion hit ``max_tokens`` so we do not silently save bad artefacts."""
    if finish_reason != "length":
        return
    allowed = os.environ.get("DEEPSEEK_ALLOW_TRUNCATED", "").strip().lower()
    if allowed in ("1", "true", "yes"):
        log(
            f"[{label}] DEEPSEEK_ALLOW_TRUNCATED=1 — saving truncated reply anyway "
            "(downstream stages may fail)."
        )
        return
    sys.exit(
        f"[{label}] error: response hit max_tokens (finish_reason=length). Output is truncated and "
        f"would break Stage B/C. Fix: export a higher limit, e.g. "
        f"export {token_env_var}=131072 "
        "(or disable Deep Thinking with DEEPSEEK_THINKING=0 to free tokens for CONTENT). "
        "Or intentionally set DEEPSEEK_ALLOW_TRUNCATED=1."
    )


# ---------- skeleton ------------------------------------------------------------


def create_skeleton(crime_root: pathlib.Path, story: str, *, overwrite: bool = False) -> pathlib.Path:
    """Mirror helper/create-story-skelton step1_create."""
    dest = crime_root / "stories" / story
    template_dir = crime_root / "bifuracted-template"

    if dest.exists():
        if not overwrite:
            return dest
        shutil.rmtree(dest)

    dest.mkdir(parents=True, exist_ok=False)
    tmpl_out = dest / "template"
    tmpl_out.mkdir(parents=True, exist_ok=True)

    write(dest / "FULL_STORY.txt", "")
    write(dest / f"output_config_{story}.md", "")
    write(dest / f"output_story_breakdown_{story}.md", "")
    write(dest / "prompt.txt", "")

    if not template_dir.is_dir():
        sys.exit(f"error: missing template dir {template_dir}")

    for src in sorted(template_dir.iterdir()):
        if not src.is_file():
            continue
        base_lc = src.name.lower()
        if base_lc == "readme.md":
            continue
        base = src.name
        if base == "stage-a-story-config.md":
            shutil.copy(src, tmpl_out / f"STORY_Config_{story}.md")
        elif base == "stage-b-scene-breakdown.md":
            shutil.copy(src, tmpl_out / f"Story_scene_breakdown_{story}.md")
        elif base == "character.txt":
            shutil.copy(src, tmpl_out / "character.txt")
        else:
            shutil.copy(src, tmpl_out / f"{story}_{base}")

    log(f"created skeleton at {dest}")
    return dest


def sync_story_from_files(story_dir: pathlib.Path, source: pathlib.Path) -> None:
    if not source.is_file():
        sys.exit(f"error: story source missing: {source}")
    txt = read(source).strip()
    if not txt:
        sys.exit(f"error: story file is empty: {source}")
    dest_full = story_dir / "FULL_STORY.txt"
    write(dest_full, txt.strip() + "\n")
    log(f"synced FULL_STORY.txt from {source}")


# ---------- stages -------------------------------------------------------------


def run_stage_a_deepseek(
    *,
    full_story: str,
    character_lib: str,
    genre: str,
    tmpl_a: pathlib.Path,
    mirror: pathlib.Path,
    out_path: pathlib.Path,
    client_kwargs: Mapping[str, Any],
    terminal: Optional[TerminalUi] = None,
    progress: Optional[PipelineProgressTracker] = None,
) -> str:
    template = read(tmpl_a)
    static_prefix, variable_suffix = split_at_part3(template)
    body = variable_suffix
    body = replace_one(body, PH_FULL_STORY_A, full_story, "FULL_STORY (A)")
    body = replace_one(body, PH_GENRE, genre, "OPTIONAL_GENRE_OR_TONE")
    body = replace_char_lib(body, character_lib)
    write(mirror, static_prefix + body)

    if progress and progress.enabled:
        progress.stage_a_waiting_api(outfile_name=out_path.name)
    else:
        log("Stage A: calling DeepSeek...")
    text, finish_a = call_deepseek(
        system_prompt=static_prefix,
        user_prompt=body,
        max_tokens=int(os.environ.get("DEEPSEEK_MAX_TOKENS_A", "65536")),
        label="stage-a",
        terminal=terminal,
        artifact_path=out_path,
        **client_kwargs,
    )
    abort_if_truncated(finish_a, "stage-a", "DEEPSEEK_MAX_TOKENS_A")
    text = text.strip() + "\n"
    write(out_path, text)
    if progress and progress.enabled:
        progress.stage_a_finished_write(outfile_name=out_path.name)
    else:
        log(f"Stage A: wrote {out_path}")
    return text


def normalise_story_paragraphs(text: str) -> str:
    """
    Insert paragraph breaks after Hindi/Hinglish sentence-ending punctuation
    (। ? !) so the segment splitter always cuts at sentence boundaries rather
    than at arbitrary character positions inside words.

    Without this, a story delivered as one long line causes _split_even_chars
    to produce fragments like 'ें बैठे दो लोग…' at the start of a segment.
    """
    # Insert \n\n after । ? ! whether or not a space follows the punctuation.
    text = re.sub(r"([।?!])\s*(?=\S)", r"\1\n\n", text)
    # Collapse any run of 3+ blank lines to a single paragraph break.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def run_stage_b_deepseek(
    *,
    config_block: str,
    full_story: str,
    character_lib: str,
    tmpl_b: pathlib.Path,
    mirror: pathlib.Path,
    out_path: pathlib.Path,
    client_kwargs: Mapping[str, Any],
    terminal: Optional[TerminalUi] = None,
    progress: Optional[PipelineProgressTracker] = None,
    story_segments: int = 1,
    segment_overlap_chars: int = 0,
    parallel_calls: int = 1,
) -> str:
    """
    Stage B scene breakdown.

    ``story_segments`` > 1 splits FULL_STORY into balanced excerpts and runs one DeepSeek call per slice,
    appends each slice's breakdown to ``output_story_breakdown_<slug>.md`` as it completes, then rewrites
    once at the end with normalized spacing (helps avoid ``finish_reason=length`` and shows progress on disk).

    ``story_segments <= 0`` selects **auto** slice count from story length (see ``resolve_stage_b_segment_count``).
    ``parallel_calls`` controls concurrent Stage B slice requests (safe default: 4).
    """
    template = read(tmpl_b)
    static_prefix, variable_suffix = split_at_part3(template)
    max_b = int(os.environ.get("DEEPSEEK_MAX_TOKENS_B", "65536"))
    full_story = normalise_story_paragraphs(full_story)
    n_seg = resolve_stage_b_segment_count(full_story=full_story, requested=int(story_segments))

    def build_body(story_slot: str) -> str:
        body = variable_suffix
        body = replace_one(body, PH_CONFIG, config_block, "STORY_CONFIG_BLOCK (B)")
        body = replace_one(body, PH_FULL_STORY_B, story_slot, "FULL_STORY (B)")
        body = replace_char_lib(body, character_lib)
        return body + "\n\n" + STAGE_B_HARD_CEILING_BANNER

    if n_seg <= 1:
        body = build_body(full_story.strip())
        write(mirror, static_prefix + body)

        if progress and progress.enabled:
            progress.stage_b_waiting_api(outfile_name=out_path.name)
        else:
            log("Stage B: calling DeepSeek...")
        text, finish_b = call_deepseek(
            system_prompt=static_prefix,
            user_prompt=body,
            max_tokens=max_b,
            label="stage-b",
            terminal=terminal,
            artifact_path=out_path,
            **client_kwargs,
        )
        abort_if_truncated(finish_b, "stage-b", "DEEPSEEK_MAX_TOKENS_B")
        single, _junk = strip_stage_b_slice_scaffolding(text.strip())
        text = single.strip() + "\n"
        text = repair_stage_b_hindi_ceiling(
            text,
            client_kwargs=client_kwargs,
            terminal=terminal,
            max_tokens=max_b,
        )
        text = renumber_stage_b_scenes(text)
        write(out_path, text)
        if progress and progress.enabled:
            progress.stage_b_finished_write(outfile_name=out_path.name)
        else:
            log(f"Stage B: wrote {out_path}")
        return text

    raw_slices = split_story_into_balanced_segments(full_story, n_seg)
    overlap_use = max(0, int(segment_overlap_chars))
    slices = apply_story_segment_overlap(raw_slices, overlap_use)
    seg_total = len(slices)
    parallel_workers = max(1, min(seg_total, int(parallel_calls)))
    log(
        f"Stage B: multi-call mode — {seg_total} story slice(s); overlap≈{overlap_use} chars; "
        f"parallel={parallel_workers} · "
        f"merge → {out_path.name}"
    )

    merged_chunks: list[str] = []
    scenes_through = 0
    scaffold_total = 0
    # Truncate so reruns start clean; each successful slice is appended right away (watch file grow mid-run).
    write(out_path, "")

    def append_slice_chunk(slice_idx: int, chunk: str) -> None:
        nonlocal scenes_through
        if chunk:
            merged_chunks.append(chunk)
            cumulative = "\n\n".join(merged_chunks)
            scenes_through = parse_scene_count(cumulative)
            already = out_path.is_file() and out_path.stat().st_size > 0
            with out_path.open("a", encoding="utf-8") as af:
                if already:
                    af.write("\n\n")
                af.write(chunk)
            try:
                sz = out_path.stat().st_size
            except OSError:
                sz = 0
            log(
                f"Stage B: slice {slice_idx + 1}/{seg_total} appended to {out_path.name} "
                f"(~{len(chunk)} chars this call · file ≈{sz} bytes · cumulative Scene≈{scenes_through})"
            )
        else:
            log(f"WARN: Stage B slice {slice_idx + 1}/{seg_total} returned empty text; skipping append")

    if parallel_workers <= 1:
        for i, slice_text in enumerate(slices):
            banner = stage_b_pipeline_split_banner(i, seg_total, scenes_through)
            story_payload = slice_text.strip() + "\n\n" + banner
            body = build_body(story_payload)
            write(mirror, static_prefix + body)

            label = f"stage-b slice {i + 1}/{seg_total}"
            note = f"story slice {i + 1}/{seg_total}"
            if progress and progress.enabled:
                progress.stage_b_waiting_api(outfile_name=out_path.name, segment_note=note)
            else:
                log(f"Stage B: slice {i + 1}/{seg_total} — calling DeepSeek...")

            text, finish_b = call_deepseek(
                system_prompt=static_prefix,
                user_prompt=body,
                max_tokens=max_b,
                label=label,
                terminal=terminal,
                artifact_path=out_path,
                **client_kwargs,
            )
            abort_if_truncated(finish_b, label, "DEEPSEEK_MAX_TOKENS_B")
            chunk_raw = text.strip()
            chunk, scaffold_dropped = strip_stage_b_slice_scaffolding(chunk_raw)
            if chunk_raw and scaffold_dropped:
                scaffold_total += scaffold_dropped
            append_slice_chunk(i, chunk)
    else:
        # Keep output order stable while running DeepSeek calls concurrently.
        queued_chunks: dict[int, str] = {}
        next_to_append = 0

        def run_slice(idx: int, slice_text: str) -> tuple[int, str, Optional[str]]:
            banner = stage_b_pipeline_split_banner(idx, seg_total, 0)
            # region agent log
            _debug_log(
                "H6",
                "deepseek_pipeline.py:run_stage_b_deepseek:run_slice:banner",
                "scenes_locked_through hardcoded to 0 for every parallel slice",
                {
                    "idx": idx,
                    "seg_total": seg_total,
                    "scenes_locked_through_passed": 0,
                    "banner_says_start_at_1": "Number scenes starting at Scene 1" in banner,
                },
            )
            # endregion agent log
            story_payload = slice_text.strip() + "\n\n" + banner
            body = build_body(story_payload)
            label = f"stage-b slice {idx + 1}/{seg_total}"
            text, finish_b = call_deepseek(
                system_prompt=static_prefix,
                user_prompt=body,
                max_tokens=max_b,
                label=label,
                terminal=terminal,
                artifact_path=out_path,
                **client_kwargs,
            )
            return idx, text, finish_b

        with ThreadPoolExecutor(max_workers=parallel_workers) as ex:
            fut_to_idx = {}
            for i, slice_text in enumerate(slices):
                note = f"story slice {i + 1}/{seg_total}"
                if progress and progress.enabled:
                    progress.stage_b_waiting_api(outfile_name=out_path.name, segment_note=note)
                else:
                    log(f"Stage B: slice {i + 1}/{seg_total} — queued for DeepSeek...")
                fut = ex.submit(run_slice, i, slice_text)
                fut_to_idx[fut] = i

            for fut in as_completed(fut_to_idx):
                i = fut_to_idx[fut]
                label = f"stage-b slice {i + 1}/{seg_total}"
                idx, text, finish_b = fut.result()
                abort_if_truncated(finish_b, label, "DEEPSEEK_MAX_TOKENS_B")
                chunk_raw = text.strip()
                chunk, scaffold_dropped = strip_stage_b_slice_scaffolding(chunk_raw)
                if chunk_raw and scaffold_dropped:
                    scaffold_total += scaffold_dropped
                queued_chunks[idx] = chunk

                # region agent log
                _first_scene_nums = [int(m.group(1)) for m in re.finditer(r'^--- Scene (\d+)', chunk, re.M)]
                _debug_log(
                    "H7",
                    "deepseek_pipeline.py:run_stage_b_deepseek:parallel:slice-result",
                    "actual scene numbers a parallel slice returned (does model literally start at 1?)",
                    {
                        "idx": idx,
                        "scene_numbers_in_chunk": _first_scene_nums[:5] + (["..."] if len(_first_scene_nums) > 5 else []),
                        "first_scene_num": _first_scene_nums[0] if _first_scene_nums else None,
                        "last_scene_num": _first_scene_nums[-1] if _first_scene_nums else None,
                        "count": len(_first_scene_nums),
                    },
                )
                # endregion agent log

                while next_to_append in queued_chunks:
                    append_slice_chunk(next_to_append, queued_chunks.pop(next_to_append))
                    next_to_append += 1

    merged_flat = "\n\n".join(merged_chunks).strip()
    merged, final_drop = strip_stage_b_slice_scaffolding(merged_flat)
    scaffold_total += final_drop
    merged = merged.strip() + "\n"

    # region agent log
    _all_nums = [int(m.group(1)) for m in re.finditer(r'^--- Scene (\d+)', merged, re.M)]
    _restarts = [
        {"index": i, "prev": _all_nums[i - 1], "next": _all_nums[i]}
        for i in range(1, len(_all_nums))
        if _all_nums[i] < _all_nums[i - 1]
    ]
    from collections import Counter as _Counter
    _dupe_counts = _Counter(_all_nums)
    _dupes = sorted(n for n, v in _dupe_counts.items() if v > 1)
    _debug_log(
        "H8",
        "deepseek_pipeline.py:run_stage_b_deepseek:merged-scene-sequence",
        "merged scene-number sequence before renumber (looking for restart/overlap matching parallel-slice bug)",
        {
            "parallel_workers": parallel_workers,
            "seg_total": seg_total,
            "total_headings": len(_all_nums),
            "unique_headings": len(_dupe_counts),
            "duplicate_numbers": _dupes,
            "restart_points": _restarts,
        },
    )
    # endregion agent log

    if scaffold_total:
        log(f"Stage B merge cleanup removed {scaffold_total} scaffolding line(s)")
    if parse_scene_count(merged) <= 0:
        sys.exit(
            "error: merged Stage B output has no 'Scene N' markers — "
            "try adjusting stage_b_story_segments or DEEPSEEK_MAX_TOKENS_B"
        )
    write(out_path, merged)
    merged = repair_stage_b_hindi_ceiling(
        merged,
        client_kwargs=client_kwargs,
        terminal=terminal,
        max_tokens=max_b,
    )
    merged = renumber_stage_b_scenes(merged)
    write(out_path, merged)
    if progress and progress.enabled:
        progress.stage_b_finished_write(outfile_name=out_path.name)
    else:
        log(f"Stage B: wrote merged breakdown ({seg_total} API calls) → {out_path}")
    return merged


def _build_stage_c_request_parts(
    *,
    tmpl_c: pathlib.Path,
    mirror: pathlib.Path,
    config_block: str,
    breakdown: str,
    character_lib: str,
    scene_range_example: str,
) -> tuple[str, str, str]:
    """Return (static_prefix, cached_context, scene_range_tail) for Stage C API calls."""
    template = read(tmpl_c)
    static_prefix, variable_suffix = split_at_part3(template)
    body_pre = variable_suffix
    body_pre = replace_one(body_pre, PH_CONFIG, config_block, "STORY_CONFIG_BLOCK (C)")
    body_pre = replace_one(body_pre, PH_BREAKDOWN, breakdown, "LOCKED_SCENE_BREAKDOWN (C)")
    body_pre = replace_char_lib(body_pre, character_lib)
    sr_idx = body_pre.find("SCENE_RANGE:")
    if sr_idx < 0:
        sys.exit("error: 'SCENE_RANGE:' label not found in Stage C template")
    cached_context = body_pre[:sr_idx]
    scene_range_tail = body_pre[sr_idx:]
    if PH_SCENE_RANGE not in scene_range_tail:
        sys.exit("error: SCENE_RANGE placeholder not found")
    first_filled = static_prefix + body_pre.replace(PH_SCENE_RANGE, scene_range_example, 1)
    write(mirror, first_filled)
    return static_prefix, cached_context, scene_range_tail


def _extract_stage_b_scene_block_by_index(breakdown: str, scene_num: int) -> str:
    """Return the Nth scene block (1-based) from a Stage B breakdown."""
    parsed = split_stage_b_by_scene_headings(breakdown)
    if not parsed:
        return ""
    _, scenes = parsed
    if 1 <= scene_num <= len(scenes):
        return scenes[scene_num - 1].strip()
    return ""


def _fetch_stage_c_single_scene_fallback(
    *,
    scene_num: int,
    breakdown: str,
    static_prefix: str,
    cached_context: str,
    scene_range_tail: str,
    max_tokens: int,
    label: str,
    out_path: pathlib.Path,
    client_kwargs: Mapping[str, Any],
    terminal: Optional[TerminalUi],
) -> Optional[str]:
    """Last-resort: ask DeepSeek for one missing scene using its breakdown excerpt."""
    scene_block = _extract_stage_b_scene_block_by_index(breakdown, scene_num)
    if not scene_block:
        return None

    scene_range = f"Scene {scene_num} ONLY"
    user_text = scene_range_tail.replace(PH_SCENE_RANGE, scene_range, 1)
    extra = (
        f"\n\nPIPELINE SINGLE-SCENE FALLBACK:\n"
        f"You MUST output exactly one scene block: --- Scene {scene_num} / ~M ---\n"
        f"Do NOT skip this scene. Do NOT use letter suffixes (no 10a/10b).\n"
        f"LOCKED SCENE BREAKDOWN excerpt for this scene:\n{scene_block}\n"
    )
    combined_user = cached_context + user_text + extra
    attempt_label = f"{label} (Scene {scene_num} fallback)"

    text, finish_c = call_deepseek(
        system_prompt=static_prefix,
        user_prompt=combined_user,
        max_tokens=max_tokens,
        label=attempt_label,
        terminal=terminal,
        artifact_path=out_path,
        **client_kwargs,
    )
    abort_if_truncated(finish_c, attempt_label, "DEEPSEEK_MAX_TOKENS_C")
    clean = strip_trailing_next_range(text).rstrip() + "\n\n"
    blocks = split_stage_c_prompt_blocks(clean)
    return blocks.get(scene_num)


def _fetch_stage_c_scene_blocks(
    *,
    static_prefix: str,
    cached_context: str,
    scene_range_tail: str,
    breakdown: str,
    range_start: int,
    range_end: int,
    max_tokens: int,
    label: str,
    out_path: pathlib.Path,
    client_kwargs: Mapping[str, Any],
    terminal: Optional[TerminalUi],
) -> dict[int, str]:
    """
    Call DeepSeek for Scenes range_start..range_end; retry until every scene is present
    or STAGE_C_BATCH_RETRIES is exhausted.
    """
    max_retries = max(1, getenv_int("STAGE_C_BATCH_RETRIES", default=3))
    needed = set(range(range_start, range_end + 1))
    collected: dict[int, str] = {}
    attempt = 0

    while needed and attempt < max_retries:
        attempt += 1
        req_start = min(needed)
        req_end = max(needed)
        scene_range = f"Scenes {req_start}-{req_end}"
        user_text = scene_range_tail.replace(PH_SCENE_RANGE, scene_range, 1)
        combined_user = cached_context + user_text
        attempt_label = (
            f"{label} ({scene_range}, attempt {attempt}/{max_retries})"
            if attempt > 1
            else f"{label} ({scene_range})"
        )

        # region agent log
        _debug_log(
            "H4",
            "deepseek_pipeline.py:_fetch_stage_c_scene_blocks:pre-call",
            "window/attempt math before API call",
            {
                "range_start": range_start,
                "range_end": range_end,
                "attempt": attempt,
                "needed_sorted": sorted(needed),
                "req_start": req_start,
                "req_end": req_end,
                "scene_range": scene_range,
                "cached_context_len": len(cached_context),
            },
        )
        # endregion agent log

        text, finish_c = call_deepseek(
            system_prompt=static_prefix,
            user_prompt=combined_user,
            max_tokens=max_tokens,
            label=attempt_label,
            terminal=terminal,
            artifact_path=out_path,
            **client_kwargs,
        )
        abort_if_truncated(finish_c, attempt_label, "DEEPSEEK_MAX_TOKENS_C")

        # region agent log
        _debug_log(
            "H2",
            "deepseek_pipeline.py:_fetch_stage_c_scene_blocks:raw-response",
            "raw model text before parsing/stripping",
            {
                "attempt": attempt,
                "req_start": req_start,
                "req_end": req_end,
                "finish_reason": finish_c,
                "raw_len": len(text),
                "raw_head": text[:400],
                "raw_tail": text[-400:],
            },
        )
        # endregion agent log

        clean = strip_trailing_next_range(text).rstrip() + "\n\n"
        min_chars = _stage_c_min_chars_for_range(req_start, req_end)

        # region agent log
        _debug_log(
            "H5",
            "deepseek_pipeline.py:_fetch_stage_c_scene_blocks:length-check",
            "clean length vs min_chars threshold",
            {
                "attempt": attempt,
                "clean_len": len(clean),
                "min_chars": min_chars,
                "threshold_035": min_chars * 0.35,
                "below_threshold": len(clean) < min_chars * 0.35,
            },
        )
        # endregion agent log

        if len(clean) < min_chars * 0.35:
            log(
                f"WARN: [{attempt_label}] reply very short ({len(clean)} chars; "
                f"expected roughly ≥{min_chars})"
            )

        blocks = split_stage_c_prompt_blocks(clean)

        # region agent log
        _debug_log(
            "H2",
            "deepseek_pipeline.py:_fetch_stage_c_scene_blocks:parsed-vs-breakdown",
            "per-scene parsed Hindi vs Stage B breakdown Hindi (match check)",
            {
                "attempt": attempt,
                "parsed_scene_numbers": sorted(blocks.keys()),
                "compare": [
                    {
                        "scene": n,
                        "breakdown_hindi_head": (
                            (
                                re.search(
                                    r"Hindi line:\s*\n(.+?)(?=\n\n|\Z)",
                                    _extract_stage_b_scene_block_by_index(breakdown, n),
                                    re.DOTALL,
                                ).group(1).strip()[:90]
                                if re.search(
                                    r"Hindi line:\s*\n(.+?)(?=\n\n|\Z)",
                                    _extract_stage_b_scene_block_by_index(breakdown, n),
                                    re.DOTALL,
                                )
                                else None
                            )
                        ),
                        "parsed_hindi_head": (
                            (
                                m2.group(1).strip()[:90]
                                if (
                                    m2 := re.search(
                                        r"Hindi line:\s*\n(.+?)(?=\n\n|\Z)", blocks[n], re.DOTALL
                                    )
                                )
                                else None
                            )
                        ),
                    }
                    for n in sorted(blocks.keys())
                    if n in needed
                ],
            },
        )
        # endregion agent log

        for n, block in blocks.items():
            if n in needed:
                collected[n] = block
        still = sorted(needed - set(collected))
        if still:
            log(
                f"WARN: [{attempt_label}] missing scene(s) {still} "
                f"({len(collected)}/{range_end - range_start + 1} collected for window)"
            )
            needed = set(still)
            continue
        needed = set()

    disable_single_scene_fallback = os.environ.get(
        "STAGE_C_DISABLE_SINGLE_SCENE_FALLBACK", ""
    ).strip().lower() in ("1", "true", "yes")

    if needed and not disable_single_scene_fallback:
        missing = sorted(needed)
        for scene_n in missing:
            block = _fetch_stage_c_single_scene_fallback(
                scene_num=scene_n,
                breakdown=breakdown,
                static_prefix=static_prefix,
                cached_context=cached_context,
                scene_range_tail=scene_range_tail,
                max_tokens=max_tokens,
                label=label,
                out_path=out_path,
                client_kwargs=client_kwargs,
                terminal=terminal,
            )
            if block:
                collected[scene_n] = block
                needed.discard(scene_n)
                log(f"Stage C: single-scene fallback recovered Scene {scene_n}")

    if needed:
        missing = sorted(needed)
        if disable_single_scene_fallback:
            log(
                "WARN: STAGE_C_DISABLE_SINGLE_SCENE_FALLBACK=1, "
                "skipping per-scene recovery."
            )
        sys.exit(
            f"error: Stage C could not produce scene(s) {missing} for {label} "
            f"after {max_retries} attempt(s). "
            "Try a smaller scene_batch, raise DEEPSEEK_MAX_TOKENS_C, or run with --fill-prompt-gaps."
        )
    return collected


def run_stage_c_deepseek(
    *,
    tmpl_c: pathlib.Path,
    mirror: pathlib.Path,
    config_block: str,
    breakdown: str,
    character_lib: str,
    batch_size: int,
    out_path: pathlib.Path,
    client_kwargs: Mapping[str, Any],
    terminal: Optional[TerminalUi] = None,
    progress: Optional[PipelineProgressTracker] = None,
    parallel_batches: int = 1,
) -> None:
    total = parse_scene_count(breakdown)
    if total <= 0:
        sys.exit("error: could not detect any 'Scene <N>' markers in Stage B output")
    estimated_batches = max(1, (total + batch_size - 1) // batch_size)
    if progress and progress.enabled:
        progress.stage_c_prepare(
            total_scenes=total,
            batch_size=batch_size,
            batches=estimated_batches,
        )
    else:
        log(f"Stage C: detected {total} scenes; batch size = {batch_size}")

    static_prefix, cached_context, scene_range_tail = _build_stage_c_request_parts(
        tmpl_c=tmpl_c,
        mirror=mirror,
        config_block=config_block,
        breakdown=breakdown,
        character_lib=character_lib,
        scene_range_example=f"Scenes 1-{min(batch_size, total)}",
    )

    max_c = int(os.environ.get("DEEPSEEK_MAX_TOKENS_C", "65536"))
    write(out_path, "")
    saved_max = 0

    windows: list[tuple[int, int, int, str]] = []
    cur = 1
    idx = 0
    while cur <= total:
        idx += 1
        end = min(cur + batch_size - 1, total)
        windows.append((idx, cur, end, f"Scenes {cur}-{end}"))
        cur = end + 1

    parallel_workers = max(1, min(int(parallel_batches), len(windows)))
    if parallel_workers > 1:
        log(
            f"Stage C: parallel mode enabled — windows={len(windows)}, "
            f"workers={parallel_workers}, batch_size={batch_size}"
        )

    def fetch_window(window: tuple[int, int, int, str]) -> tuple[int, int, int, dict[int, str], int]:
        batch_idx, start, end, _scene_range = window
        label = f"stage-c batch {batch_idx}/{estimated_batches}"
        collected = _fetch_stage_c_scene_blocks(
            static_prefix=static_prefix,
            cached_context=cached_context,
            scene_range_tail=scene_range_tail,
            breakdown=breakdown,
            range_start=start,
            range_end=end,
            max_tokens=max_c,
            label=label,
            out_path=out_path,
            client_kwargs=client_kwargs,
            terminal=terminal,
        )
        chars_written = sum(len(b) for b in collected.values())
        return batch_idx, start, end, collected, chars_written

    if parallel_workers <= 1:
        for batch_idx, start, end, scene_range in windows:
            if progress and progress.enabled:
                progress.stage_c_batch_waiting_api(
                    batch_idx=batch_idx,
                    batches=estimated_batches,
                    cur_scene=start,
                    total_scenes=total,
                    range_label=scene_range,
                )
            else:
                log_stage_c_progress(
                    scenes_done_through=saved_max,
                    total_scenes=total,
                    batch_idx=batch_idx,
                    estimated_batches=estimated_batches,
                    cur_scene=start,
                    batch_end_scene=end,
                    phase=f"calling DeepSeek for {scene_range}",
                )

            _idx, _start, _end, collected, chars_written = fetch_window((batch_idx, start, end, scene_range))
            with out_path.open("a", encoding="utf-8") as f:
                for n in range(start, end + 1):
                    f.write(collected[n])

            saved_max = max(saved_max, max(collected))
            if progress and progress.enabled:
                progress.stage_c_batch_appended(
                    batch_idx=batch_idx,
                    batches=estimated_batches,
                    scenes_saved_through=saved_max,
                    total_scenes=total,
                    chars_written=chars_written,
                    extra_note="",
                )
            else:
                log_stage_c_progress(
                    scenes_done_through=saved_max,
                    total_scenes=total,
                    batch_idx=batch_idx,
                    estimated_batches=estimated_batches,
                    cur_scene=min(end + 1, total + 1),
                    batch_end_scene=end,
                    phase=f"appended ≈{chars_written} chars ({len(collected)} scenes)",
                )
    else:
        pending_results: dict[int, tuple[int, int, dict[int, str], int]] = {}
        next_batch_to_flush = 1
        completed = 0
        with ThreadPoolExecutor(max_workers=parallel_workers) as ex:
            fut_to_window = {}
            for window in windows:
                batch_idx, start, end, scene_range = window
                if progress and progress.enabled:
                    progress.stage_c_batch_waiting_api(
                        batch_idx=batch_idx,
                        batches=estimated_batches,
                        cur_scene=start,
                        total_scenes=total,
                        range_label=scene_range,
                    )
                else:
                    log_stage_c_progress(
                        scenes_done_through=saved_max,
                        total_scenes=total,
                        batch_idx=batch_idx,
                        estimated_batches=estimated_batches,
                        cur_scene=start,
                        batch_end_scene=end,
                        phase=f"queued DeepSeek call for {scene_range}",
                    )
                fut = ex.submit(fetch_window, window)
                fut_to_window[fut] = window

            for fut in as_completed(fut_to_window):
                batch_idx, start, end, collected, chars_written = fut.result()
                pending_results[batch_idx] = (start, end, collected, chars_written)
                completed += 1

                while next_batch_to_flush in pending_results:
                    flush_start, flush_end, flush_collected, flush_chars = pending_results.pop(next_batch_to_flush)
                    with out_path.open("a", encoding="utf-8") as f:
                        for n in range(flush_start, flush_end + 1):
                            f.write(flush_collected[n])
                    saved_max = max(saved_max, max(flush_collected))
                    extra = f"parallel complete {completed}/{estimated_batches}"
                    if progress and progress.enabled:
                        progress.stage_c_batch_appended(
                            batch_idx=next_batch_to_flush,
                            batches=estimated_batches,
                            scenes_saved_through=saved_max,
                            total_scenes=total,
                            chars_written=flush_chars,
                            extra_note=extra,
                        )
                    else:
                        log_stage_c_progress(
                            scenes_done_through=saved_max,
                            total_scenes=total,
                            batch_idx=next_batch_to_flush,
                            estimated_batches=estimated_batches,
                            cur_scene=min(flush_end + 1, total + 1),
                            batch_end_scene=flush_end,
                            phase=(
                                f"appended ≈{flush_chars} chars ({len(flush_collected)} scenes) · {extra}"
                            ),
                        )
                    next_batch_to_flush += 1

    on_disk = parse_stage_c_scene_numbers(read(out_path))
    still_missing = find_missing_prompt_scenes(read(out_path), total)
    if still_missing:
        sys.exit(
            f"error: Stage C finished but prompt.txt is missing scene(s): "
            f"{still_missing[:20]}{'...' if len(still_missing) > 20 else ''}"
        )
    if not (progress and progress.enabled):
        log(f"Stage C: complete; wrote {out_path} ({len(on_disk)} scenes)")


def run_stage_c_fill_prompt_gaps(
    *,
    tmpl_c: pathlib.Path,
    mirror: pathlib.Path,
    config_block: str,
    breakdown: str,
    character_lib: str,
    batch_size: int,
    out_path: pathlib.Path,
    client_kwargs: Mapping[str, Any],
    terminal: Optional[TerminalUi] = None,
    progress: Optional[PipelineProgressTracker] = None,
) -> None:
    """Regenerate only missing scenes in an existing prompt.txt and rewrite the file in order."""
    total = parse_scene_count(breakdown)
    if total <= 0:
        sys.exit("error: could not detect any 'Scene <N>' markers in Stage B output")
    if not out_path.is_file() or out_path.stat().st_size == 0:
        sys.exit(f"error: {out_path} is empty — run full Stage C first, not --fill-prompt-gaps")

    existing = read(out_path)
    blocks = split_stage_c_prompt_blocks(existing)
    missing = find_missing_prompt_scenes(existing, total)
    if not missing:
        log(f"Stage C fill-gaps: {out_path.name} already has all {total} scenes")
        return

    ranges = _missing_scene_ranges(missing)
    log(
        f"Stage C fill-gaps: {len(missing)} missing scene(s) in {len(ranges)} range(s): "
        + ", ".join(f"{a}-{b}" for a, b in ranges)
    )

    static_prefix, cached_context, scene_range_tail = _build_stage_c_request_parts(
        tmpl_c=tmpl_c,
        mirror=mirror,
        config_block=config_block,
        breakdown=breakdown,
        character_lib=character_lib,
        scene_range_example=f"Scenes {missing[0]}-{missing[-1]}",
    )
    max_c = int(os.environ.get("DEEPSEEK_MAX_TOKENS_C", "65536"))

    # region agent log
    _probe_scenes = [n for n in (62, 64, 71, 74, 75) if n in set(missing)]
    _probe_results = {}
    for _n in _probe_scenes:
        _blk = _extract_stage_b_scene_block_by_index(breakdown, _n)
        _hm = re.search(r"Hindi line:\s*\n(.+?)(?=\n\n|\Z)", _blk, re.DOTALL)
        _hindi = _hm.group(1).strip() if _hm else ""
        _probe_results[_n] = {
            "breakdown_hindi_head": _hindi[:90],
            "hindi_found_in_cached_context": bool(_hindi) and _hindi[:40] in cached_context,
        }
    _debug_log(
        "H1",
        "deepseek_pipeline.py:run_stage_c_fill_prompt_gaps:cached-context-check",
        "does cached_context sent to Stage C contain the correct breakdown Hindi for target scenes",
        {
            "missing_scenes": missing,
            "ranges": ranges,
            "cached_context_len": len(cached_context),
            "breakdown_len": len(breakdown),
            "probe": _probe_results,
        },
    )
    # endregion agent log

    for gap_i, (g0, g1) in enumerate(ranges, start=1):
        sub = g0
        while sub <= g1:
            sub_end = min(sub + batch_size - 1, g1)
            label = f"stage-c fill-gaps {gap_i}/{len(ranges)}"
            if progress and progress.enabled:
                progress.stage_c_batch_waiting_api(
                    batch_idx=gap_i,
                    batches=len(ranges),
                    cur_scene=sub,
                    total_scenes=total,
                    range_label=f"Scenes {sub}-{sub_end} (fill)",
                )
            collected = _fetch_stage_c_scene_blocks(
                static_prefix=static_prefix,
                cached_context=cached_context,
                scene_range_tail=scene_range_tail,
                breakdown=breakdown,
                range_start=sub,
                range_end=sub_end,
                max_tokens=max_c,
                label=label,
                out_path=out_path,
                client_kwargs=client_kwargs,
                terminal=terminal,
            )
            blocks.update(collected)
            chars_written = sum(len(b) for b in collected.values())
            saved_max = max(blocks)
            if progress and progress.enabled:
                progress.stage_c_batch_appended(
                    batch_idx=gap_i,
                    batches=len(ranges),
                    scenes_saved_through=saved_max,
                    total_scenes=total,
                    chars_written=chars_written,
                    extra_note=f"filled {sub}-{sub_end}",
                )
            else:
                log(
                    f"Stage C fill-gaps: wrote scenes {sub}-{sub_end} "
                    f"(≈{chars_written} chars)"
                )
            sub = sub_end + 1

    write(out_path, merge_stage_c_prompt_blocks(blocks, total))
    log(f"Stage C fill-gaps: merged prompt → {out_path} ({total} scenes)")


def build_client_kw(
    *,
    api_key: str,
    base_url: str,
    model: str,
    temperature: float,
    reasoning_effort: Optional[str],
    enable_search: bool,
    thinking: bool,
) -> dict[str, Any]:
    # When Deep Thinking is on, upstream may ignore temperature; we still omit
    # temperature inside call_deepseek for that case.
    return dict(
        api_key=api_key,
        base_url=base_url.rstrip("/"),
        model=model,
        temperature=temperature,
        reasoning_effort=reasoning_effort if thinking else None,
        enable_search=enable_search,
        thinking=thinking,
    )


def main() -> int:
    pipeline_t0 = time.monotonic()
    pipeline_wall_start = time.time()
    log(
        "TIMING pipeline start "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pipeline_wall_start))} (local)"
    )

    stage_elapsed_sec: dict[str, float] = {}
    stage_mode: dict[str, str] = {
        "stage_a": "not-run",
        "stage_b": "not-run",
        "stage_c": "not-run",
        "derivatives": "not-run",
    }

    def _mark_stage_timing(stage_key: str, stage_t0: float, mode: str) -> None:
        stage_elapsed_sec[stage_key] = max(0.0, time.monotonic() - stage_t0)
        stage_mode[stage_key] = mode

    def _log_pipeline_timing_footer() -> None:
        wall_end = time.time()
        dt = time.monotonic() - pipeline_t0
        log("TIMING stage summary:")
        for key, label in (
            ("stage_a", "Stage A"),
            ("stage_b", "Stage B"),
            ("stage_c", "Stage C"),
            ("derivatives", "Derivatives"),
        ):
            mode = stage_mode.get(key, "not-run")
            sec = stage_elapsed_sec.get(key)
            if sec is None:
                log(f"TIMING {label}: not run ({mode})")
            else:
                log(f"TIMING {label}: {sec:.1f}s ({sec / 60.0:.2f} min) [{mode}]")
        log(
            "TIMING pipeline end "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(wall_end))} (local) · "
            f"elapsed {dt:.1f}s ({dt / 60.0:.2f} min)"
        )

    atexit.register(_log_pipeline_timing_footer)

    here = pathlib.Path(__file__).resolve().parent
    crime_root_default = here.parent
    repo_root = crime_root_default.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    load_repo_dotenv(repo_root)

    skip_ini_argv = "--skip-ini" in sys.argv
    if not skip_ini_argv:
        cfg_explicit = getenv_nonempty("DEEPSEEK_CONFIG_PATH")
        if cfg_explicit:
            bootstrap_deepseek_ini(pathlib.Path(cfg_explicit).expanduser())
        else:
            bootstrap_deepseek_ini(crime_root_default / "deepseek.config.example.ini")

    _story_file_env = getenv_nonempty("DEEPSEEK_STORY_FILE")
    story_source_default = (
        pathlib.Path(_story_file_env).expanduser().resolve()
        if _story_file_env is not None
        else None
    )
    _thinking_raw_env = getenv_nonempty("DEEPSEEK_THINKING")
    thinking_default = (
        True
        if _thinking_raw_env is None
        else _thinking_raw_env.lower() not in ("0", "false", "no", "off")
    )
    reasoning_default_ini = getenv_nonempty("DEEPSEEK_REASONING_EFFORT")
    reasoning_default = reasoning_default_ini if reasoning_default_ini else None
    _genre_ini = getenv_nonempty("DEEPSEEK_GENRE") or ""
    _max_step_ini = getenv_nonempty("DEEPSEEK_MAX_STEP")
    try:
        max_step_default = int(_max_step_ini) if _max_step_ini else 4
        if max_step_default not in (1, 2, 3, 4):
            sys.exit(f"error: DEEPSEEK_MAX_STEP must be between 1 and 4 ({max_step_default})")
    except ValueError:
        sys.exit("error: DEEPSEEK_MAX_STEP must be a whole number")
    _batch_ini = getenv_nonempty("STAGE_C_BATCH")
    try:
        batch_default = int(_batch_ini) if _batch_ini else 8
    except ValueError:
        sys.exit("error: STAGE_C_BATCH must be a whole number")

    parser = argparse.ArgumentParser(
        description=(
            "Crime-section DeepSeek pipeline. Defaults load from crime-section/deepseek.config.example.ini "
            "(edit there) unless DEEPSEEK_CONFIG_PATH or --config points elsewhere."
        ),
    )
    parser.add_argument(
        "--story",
        metavar="SLUG",
        default=os.environ.get("PIPELINE_STORY", ""),
        help=(
            "Story slug folder under crime-section/stories/. "
            "If omitted on the CLI, PIPELINE_STORY from the environment is used."
        ),
    )
    parser.add_argument(
        "--crime-root",
        type=pathlib.Path,
        default=crime_root_default,
        help="Path to crime-section (default: parent of helper/)",
    )
    parser.add_argument(
        "--story-source",
        type=pathlib.Path,
        default=story_source_default,
        help="Story text path (INI pipeline.story_txt_path → DEEPSEEK_STORY_FILE). Blank → story-to-run/story.txt",
    )
    parser.add_argument(
        "--max-step",
        type=int,
        choices=(1, 2, 3, 4),
        default=max_step_default,
        help="INI [pipeline].max_step or DEEPSEEK_MAX_STEP.",
    )
    parser.add_argument("--model", default=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"))
    parser.add_argument(
        "--base-url",
        default=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        help="OpenAI-compatible base URL",
    )
    parser.add_argument(
        "--genre",
        default=_genre_ini,
        help="INI [genre_hint].mood_hint / DEEPSEEK_GENRE",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=batch_default,
        help="INI token_budget.scene_batch / STAGE_C_BATCH",
    )
    parser.add_argument(
        "--use-character-lib",
        action=argparse.BooleanOptionalAction,
        default=getenv_bool("DEEPSEEK_USE_CHARACTER_LIB"),
        help="INI pipeline.use_character_library",
    )
    parser.add_argument(
        "--force",
        dest="force",
        action=argparse.BooleanOptionalAction,
        default=getenv_bool("FORCE", "DEEPSEEK_FORCE"),
        help="INI pipeline.force / FORCE env",
    )
    parser.add_argument(
        "--recreate-story-dir",
        dest="recreate_story_dir",
        action=argparse.BooleanOptionalAction,
        default=getenv_bool("DEEPSEEK_RECREATE_STORY"),
        help="INI pipeline.recreate_story_folder",
    )
    def env_float(var: str, default: float) -> float:
        raw = os.environ.get(var)
        if raw is None or str(raw).strip() == "":
            return default
        try:
            return float(raw)
        except ValueError:
            sys.exit(f"error: {var} must be a floating number")

    parser.add_argument(
        "--temperature",
        type=float,
        default=env_float("DEEPSEEK_TEMPERATURE", 0.3),
        help="passed for reasoner/non-thinking chats; overridden by reasoning models per API rules",
    )
    parser.add_argument(
        "--reasoning-effort",
        default=reasoning_default,
        help='INI thinking.reasoning_effort / DEEPSEEK_REASONING_EFFORT ("high", "max", …).',
    )
    parser.add_argument(
        "--thinking/--no-thinking",
        dest="thinking",
        default=thinking_default,
        help="INI thinking.enabled / DEEPSEEK_THINKING.",
    )
    parser.add_argument(
        "--web-search/--no-web-search",
        dest="deepseek_web_search",
        action=argparse.BooleanOptionalAction,
        default=getenv_bool("DEEPSEEK_ENABLE_SEARCH"),
        help="INI smart_search.internet_enabled / DEEPSEEK_ENABLE_SEARCH.",
    )
    parser.add_argument(
        "--config",
        "-c",
        dest="deepseek_ini",
        type=pathlib.Path,
        default=None,
        metavar="INI_FILE",
        help="Optional supplemental INI (still uses safe setdefault merges).",
    )
    parser.add_argument(
        "--skip-ini",
        action="store_true",
        help="Skip INI merges (default file, DEEPSEEK_CONFIG_PATH, --config layering).",
    )
    parser.add_argument(
        "--show-api-output/--hide-api-output",
        dest="show_api_output",
        action=argparse.BooleanOptionalAction,
        default=getenv_bool("DEEPSEEK_SHOW_API_OUTPUT", default=True),
        help=(
            "After each Stage A/B/C DeepSeek completion, print the assistant reply to the terminal "
            "(INI terminal.show_api_output)."
        ),
    )
    parser.add_argument(
        "--stream-api-output/--no-stream-api-output",
        dest="stream_api_output",
        action=argparse.BooleanOptionalAction,
        default=getenv_bool("DEEPSEEK_STREAM_API_OUTPUT"),
        help="Stream completion chunks live when the SDK/API allows (INI terminal.stream_api_output).",
    )
    parser.add_argument(
        "--terminal-max-chars",
        type=int,
        default=getenv_int("DEEPSEEK_TERMINAL_MAX_CHARS", default=12000),
        metavar="N",
        help="Non-stream previews: max chars printed (0 = unlimited; INI terminal.max_print_chars).",
    )
    parser.add_argument(
        "--stage-b-terminal-scenes",
        type=int,
        default=getenv_int("DEEPSEEK_STAGE_B_TERMINAL_SCENES", default=10),
        metavar="N",
        help=(
            "Stage B: print breakdown in sequential terminal chunks of N scenes (line-start headings). "
            "0 = one block. INI terminal.stage_b_terminal_scenes."
        ),
    )
    parser.add_argument(
        "--stage-b-story-segments",
        type=int,
        default=getenv_int("STAGE_B_STORY_SEGMENTS", default=1),
        metavar="N",
        help=(
            "Stage B: split FULL_STORY into N balanced slices → N breakdown API calls → merge (e.g. 10 for long "
            "scripts; try 4–10 if finish_reason=length). "
            "0 or negative = auto from length (INI token_budget.stage_b_auto_target_chars + hard cap). "
            "INI token_budget.stage_b_story_segments."
        ),
    )
    parser.add_argument(
        "--stage-b-segment-overlap",
        type=int,
        default=getenv_int("STAGE_B_SEGMENT_OVERLAP_CHARS", default=400),
        metavar="N",
        help=(
            "When Stage B uses multiple story slices: suffix-prefix overlap (chars) between slices for continuity. "
            "INI token_budget.stage_b_segment_overlap_chars. Ignored when segments=1."
        ),
    )
    parser.add_argument(
        "--stage-b-parallel-calls",
        type=int,
        default=getenv_int("STAGE_B_PARALLEL_CALLS", default=4),
        metavar="N",
        help=(
            "Stage B: run up to N slice calls in parallel (preserves merged scene order). "
            "INI token_budget.stage_b_parallel_calls / STAGE_B_PARALLEL_CALLS."
        ),
    )
    parser.add_argument(
        "--stage-c-parallel-batches",
        type=int,
        default=getenv_int("STAGE_C_PARALLEL_BATCHES", default=4),
        metavar="N",
        help=(
            "Stage C: run up to N scene windows in parallel (preserves prompt.txt scene order). "
            "INI token_budget.stage_c_parallel_batches / STAGE_C_PARALLEL_BATCHES."
        ),
    )

    parser.add_argument(
        "--progress-bar/--no-progress-bar",
        dest="terminal_progress_bar",
        action=argparse.BooleanOptionalAction,
        default=getenv_bool("DEEPSEEK_TERMINAL_PROGRESS_BAR", default=True),
        help=(
            "Show coarse overall %% plus stage/API captions on the terminal (INI terminal.show_progress_bar). "
            "Turn off alongside --hide-api-output for a nearly silent run."
        ),
    )
    parser.add_argument(
        "--fill-prompt-gaps",
        dest="fill_prompt_gaps",
        action="store_true",
        help=(
            "Stage C only: detect missing --- Scene N --- blocks in prompt.txt vs Stage B, "
            "call the API for those ranges, merge in order, and rewrite prompt.txt. "
            "Requires existing prompt.txt + breakdown (does not rerun A/B)."
        ),
    )

    args = parser.parse_args()
    crime_root = args.crime_root.resolve()

    if not args.skip_ini:
        if getattr(args, "deepseek_ini", None):
            bootstrap_deepseek_ini(pathlib.Path(args.deepseek_ini).expanduser())
        elif crime_root.resolve() != crime_root_default.resolve():
            bootstrap_deepseek_ini(crime_root / "deepseek.config.example.ini")

    enable_search = getattr(args, "deepseek_web_search", False)

    story = (args.story or "").strip()
    if not story:
        parser.error(
            "provide --story SLUG (story folder under stories/) "
            "or export PIPELINE_STORY=SLUG — see --help."
        )
    if "/" in story or ".." in story:
        sys.exit("error: --story must be a single safe path segment")

    story_source = (
        pathlib.Path(args.story_source).resolve()
        if args.story_source
        else crime_root / "story-to-run" / "story.txt"
    )

    story_dir = create_skeleton(crime_root, story, overwrite=args.recreate_story_dir)
    tmpl_dir = story_dir / "template"
    tmpl_a = crime_root / "bifuracted-template" / "stage-a-story-config.md"
    tmpl_b = crime_root / "bifuracted-template" / "stage-b-scene-breakdown.md"
    tmpl_c = crime_root / "bifuracted-template" / "stage-c-image-motion.md"

    for p in tmpl_a, tmpl_b, tmpl_c:
        if not p.is_file():
            sys.exit(f"error: missing bifuracted template {p}")

    sync_story_from_files(story_dir, story_source)

    terminal_ui = TerminalUi(
        show_completion_text=bool(args.show_api_output),
        stream_completions_to_stdout=bool(args.stream_api_output),
        max_print_chars=max(0, int(args.terminal_max_chars)),
        stage_b_terminal_scenes_per_batch=max(0, int(args.stage_b_terminal_scenes)),
        show_progress_bar=bool(args.terminal_progress_bar),
    )

    if args.max_step <= 1:
        log("--max-step 1: skeleton + synced story complete; exiting.")
        return 0

    progress = PipelineProgressTracker(max_step=args.max_step, terminal=terminal_ui)
    progress.llm_phases_prepare()

    api_key = resolve_api_key()

    reasoning = args.reasoning_effort if args.thinking else None

    ck = build_client_kw(
        api_key=api_key,
        base_url=args.base_url,
        model=args.model,
        temperature=args.temperature,
        reasoning_effort=reasoning,
        enable_search=enable_search,
        thinking=args.thinking,
    )

    full_story_path = story_dir / "FULL_STORY.txt"
    full_story = read(full_story_path).strip()
    config_path = story_dir / f"output_config_{story}.md"
    breakdown_path = story_dir / f"output_story_breakdown_{story}.md"
    prompt_path = story_dir / "prompt.txt"

    mirror_a = tmpl_dir / f"STORY_Config_{story}.md"
    mirror_b = tmpl_dir / f"Story_scene_breakdown_{story}.md"
    mirror_c = tmpl_dir / f"{story}_stage-c-image-motion.md"

    char_path = tmpl_dir / "character.txt"
    use_lib = args.use_character_lib
    character_lib = "NONE"
    if use_lib and char_path.is_file() and char_path.stat().st_size > 0:
        character_lib = read(char_path).strip()
        log(f"using character library from {char_path}")
    elif use_lib:
        log("character.txt missing or empty; using NONE")

    # -------- Stage A --------
    config_block = ""
    stage_a_t0 = time.monotonic()
    if config_path.is_file() and config_path.stat().st_size > 0 and not args.force:
        if progress.enabled:
            progress.stage_a_using_cache(outfile_name=config_path.name)
        else:
            log(f"Stage A: skipped ({config_path} already populated; use --force to redo)")
        config_block = read(config_path).strip()
        _mark_stage_timing("stage_a", stage_a_t0, "cache-hit")
    else:
        config_block = run_stage_a_deepseek(
            full_story=full_story,
            character_lib=character_lib,
            genre=args.genre,
            tmpl_a=tmpl_a,
            mirror=mirror_a,
            out_path=config_path,
            client_kwargs=ck,
            terminal=terminal_ui,
            progress=progress,
        ).strip()
        _mark_stage_timing("stage_a", stage_a_t0, "api")

    if args.max_step <= 2:
        if progress.enabled:
            progress.pipeline_complete(
                hint=f"Stopped after Stage A (--max-step 2) · {config_path.name}",
            )
        else:
            log("--max-step 2: Stage A done; exiting before Stage B.")
        return 0

    # -------- Stage B --------
    breakdown = ""
    stage_b_t0 = time.monotonic()
    if breakdown_path.is_file() and breakdown_path.stat().st_size > 0 and not args.force:
        if progress.enabled:
            progress.stage_b_using_cache(outfile_name=breakdown_path.name)
        else:
            log(f"Stage B: skipped ({breakdown_path} already populated; use --force to redo)")
        breakdown = read(breakdown_path).strip()
        # Resume loads cached Stage B without the post-merge renumber pass; letter
        # suffixes (Scene 20a/20b) make Stage C ask for a scene N that does not exist.
        normalized = renumber_stage_b_scenes(breakdown)
        if normalized != breakdown:
            write(breakdown_path, normalized)
            breakdown = normalized
        _mark_stage_timing("stage_b", stage_b_t0, "cache-hit")
    else:
        breakdown = run_stage_b_deepseek(
            config_block=config_block,
            full_story=full_story,
            character_lib=character_lib,
            tmpl_b=tmpl_b,
            mirror=mirror_b,
            out_path=breakdown_path,
            client_kwargs=ck,
            terminal=terminal_ui,
            progress=progress,
            story_segments=int(args.stage_b_story_segments),
            segment_overlap_chars=max(0, int(args.stage_b_segment_overlap)),
            parallel_calls=max(1, int(args.stage_b_parallel_calls)),
        ).strip()
        _mark_stage_timing("stage_b", stage_b_t0, "api")

    if args.max_step <= 3:
        if progress.enabled:
            progress.pipeline_complete(
                hint=f"Stopped after Stage B (--max-step 3) · {breakdown_path.name}",
            )
        else:
            log("--max-step 3: Stages A+B done; exiting before Stage C.")
        return 0

    # -------- Stage C --------
    fill_gaps = bool(getattr(args, "fill_prompt_gaps", False))
    stage_c_t0 = time.monotonic()
    if fill_gaps:
        if args.force:
            log("WARN: --fill-prompt-gaps ignores --force (existing scenes are kept)")
        if not breakdown_path.is_file():
            sys.exit(f"error: missing Stage B output {breakdown_path}")
        if not config_path.is_file():
            sys.exit(f"error: missing Stage A output {config_path}")
        run_stage_c_fill_prompt_gaps(
            tmpl_c=tmpl_c,
            mirror=mirror_c,
            config_block=config_block,
            breakdown=breakdown,
            character_lib=character_lib,
            batch_size=args.batch,
            out_path=prompt_path,
            client_kwargs=ck,
            terminal=terminal_ui,
            progress=progress,
        )
        _mark_stage_timing("stage_c", stage_c_t0, "fill-gaps")
    elif prompt_path.is_file() and prompt_path.stat().st_size > 0 and not args.force:
        log(
            f"Stage C: skipped ({prompt_path} already populated; "
            "use --force to redo, or --fill-prompt-gaps for missing scenes only)"
        )
        _mark_stage_timing("stage_c", stage_c_t0, "cache-hit")
    else:
        run_stage_c_deepseek(
            tmpl_c=tmpl_c,
            mirror=mirror_c,
            config_block=config_block,
            breakdown=breakdown,
            character_lib=character_lib,
            batch_size=args.batch,
            out_path=prompt_path,
            client_kwargs=ck,
            terminal=terminal_ui,
            progress=progress,
            parallel_batches=max(1, int(args.stage_c_parallel_batches)),
        )
        _mark_stage_timing("stage_c", stage_c_t0, "api")

    if progress.enabled:
        progress.pipeline_complete(hint=str(prompt_path))
    else:
        log("DONE")

    derivatives_t0 = time.monotonic()
    run_prompt_derivative_export(
        prompt_path,
        client_kwargs=ck,
        force=bool(args.force),
    )
    _mark_stage_timing("derivatives", derivatives_t0, "export")

    return 0


if __name__ == "__main__":
    sys.exit(main())
