#!/usr/bin/env python3
"""
Documentary Engine — AI Documentary Research & Story Engine (v2)

Standalone pipeline. Uses DeepSeek API only.
No dependency on story-agent or other repo pipelines.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE_ROOT))

from src.config import load_config  # noqa: E402
from src.deepseek_client import log  # noqa: E402
from src.input_handler import build_input, parse_queue_line  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


DEFAULT_QUEUE = ENGINE_ROOT / "queue.txt"


def load_queue(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Queue file not found: {path}")
    jobs = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        job = parse_queue_line(line, i)
        if job:
            jobs.append(job)
    return jobs


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Documentary Engine — DeepSeek multi-agent pipeline")
    p.add_argument("--queue", default=str(DEFAULT_QUEUE), help="Queue file path")
    p.add_argument("--input-type", choices=("youtube", "topic", "pdf", "article", "notes"))
    p.add_argument("--input-value", help="URL, topic text, or file path")
    p.add_argument("--duration", type=int, default=30, help="Target duration in minutes (default: 30)")
    p.add_argument("--folder", help="Output folder name under storage/")
    p.add_argument("--series-id", help="Multi-episode series ID for continuity state")
    p.add_argument("--config", type=Path, help="Path to deepseek.config.ini")
    p.add_argument("--research-only", action="store_true", help="Stop after YouTube research phase")
    p.add_argument("--resume", action="store_true", help="Reuse completed phase artifacts")
    p.add_argument("--skip-human-checkpoint", action="store_true", help="Bypass human review gate")
    p.add_argument("--from-phase", help="Force rerun from phase (extraction|timeline|characters)")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.input_type and args.input_value:
        jobs = [
            build_input(
                input_type=args.input_type,
                raw_value=args.input_value,
                duration_minutes=args.duration,
                folder_name=args.folder,
                series_id=args.series_id,
            )
        ]
    else:
        jobs = load_queue(Path(args.queue))
        if not jobs:
            log(f"No active entries in {args.queue}")
            return 1

    failed = 0
    for i, job in enumerate(jobs, 1):
        log(f"\n--- [{i}/{len(jobs)}] {job.topic}")
        try:
            run_pipeline(
                job,
                cfg=cfg,
                resume=args.resume,
                skip_human_checkpoint=args.skip_human_checkpoint,
                research_only=args.research_only,
                from_phase=args.from_phase,
            )
        except SystemExit:
            raise
        except Exception as exc:
            log(f"FAILED: {exc}")
            failed += 1
            if len(jobs) == 1:
                return 1

    if failed:
        log(f"Finished with {failed} failure(s)")
        return 1
    log("All jobs complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
