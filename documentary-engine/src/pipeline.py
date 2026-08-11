"""Multi-agent documentary pipeline orchestrator."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agents import (
    CharacterIntelligenceAgent,
    FactVerificationAgent,
    GapResearchAgent,
    KnowledgeExtractionAgent,
    RetentionReviewerAgent,
    ScriptWriterAgent,
    StoryArchitectAgent,
    VisualsAgent,
    TimelineAgent,
)
from .config import EngineConfig, load_config
from .deepseek_client import DeepSeekClient, log
from .input_handler import DocumentaryInput, build_input, save_input_manifest
from .schemas import empty_story_state, target_chars
from .youtube_research import rank_and_select_videos, save_research


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _merge_gap_facts(knowledge: dict, gap: dict) -> dict:
    new_facts = gap.get("new_facts") or []
    if not new_facts:
        return knowledge
    facts = list(knowledge.get("facts") or [])
    facts.extend(new_facts)
    knowledge["facts"] = facts
    return knowledge


def _build_transcript_bundle(research_dir: Path) -> str:
    videos = _load_json(research_dir / "videos.json")
    blocks: list[str] = []
    for entry in videos:
        filename = entry.get("filename")
        if not filename:
            continue
        path = research_dir / "transcripts" / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").strip()
        header = (
            f"=== SOURCE: {entry.get('source_id')} | {entry.get('title')} ===\n"
            f"URL: {entry.get('youtube_url')} | Views: {entry.get('view_count')}\n"
            f"ROLE: Research lead only — verify facts, do not copy narration.\n"
        )
        blocks.append(f"{header}\n{text}")
    return "\n\n---\n\n".join(blocks)


def _build_source_list(knowledge: dict, verification: dict) -> dict:
    by_confidence: dict[str, list] = {
        "verified": [],
        "probable": [],
        "unverified": [],
        "disputed": [],
    }
    for fact in knowledge.get("facts") or []:
        conf = (fact.get("confidence") or "unverified").lower()
        bucket = conf if conf in by_confidence else "unverified"
        by_confidence[bucket].append(fact)

    for item in verification.get("disputed_claims") or []:
        by_confidence["disputed"].append(item)
    for item in verification.get("unverified_claims") or []:
        by_confidence["unverified"].append(item)
    for item in verification.get("verified_claims") or []:
        by_confidence["verified"].append(item)

    return by_confidence


def _human_checkpoint(run_dir: Path, verification: dict, *, force: bool) -> str:
    checkpoint_dir = run_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    review_path = checkpoint_dir / "human_review.json"
    notes_path = checkpoint_dir / "human_review_notes.txt"
    approved_path = checkpoint_dir / "APPROVED"

    _save_json(review_path, verification)

    if approved_path.exists() and not force:
        log("Human checkpoint: APPROVED file found — continuing")
        return notes_path.read_text(encoding="utf-8").strip() if notes_path.exists() else ""

    log("")
    log("=" * 72)
    log("HUMAN CHECKPOINT — review before final script generation")
    log(f"  Fact verification: {review_path}")
    log("  Add optional notes to: " + str(notes_path))
    log("  When satisfied, create empty file: " + str(approved_path))
    log("  Re-run with --resume to continue after approval.")
    log("  Or use --skip-human-checkpoint to bypass (not recommended for sensitive topics).")
    log("=" * 72)
    raise SystemExit(0)


def _load_story_state(storage: Path, series_id: str | None) -> dict:
    if not series_id:
        return empty_story_state()
    state_path = storage / "_series" / series_id / "story_state.json"
    if state_path.exists():
        return _load_json(state_path)
    return empty_story_state(series_id)


def _save_story_state(storage: Path, series_id: str | None, state: dict) -> None:
    if not series_id:
        return
    state_dir = storage / "_series" / series_id
    state_dir.mkdir(parents=True, exist_ok=True)
    _save_json(state_dir / "story_state.json", state)


def run_pipeline(
    doc_input: DocumentaryInput,
    *,
    cfg: EngineConfig | None = None,
    resume: bool = False,
    skip_human_checkpoint: bool = False,
    research_only: bool = False,
    from_phase: str | None = None,
) -> Path:
    cfg = cfg or load_config()
    client = DeepSeekClient(cfg.deepseek)

    run_dir = cfg.pipeline.storage_root / doc_input.folder_name
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts = run_dir / "artifacts"
    artifacts.mkdir(exist_ok=True)

    save_input_manifest(run_dir, doc_input)
    story_state = _load_story_state(cfg.pipeline.storage_root, doc_input.series_id or cfg.pipeline.series_id)

    context: dict[str, Any] = {
        "topic": doc_input.topic,
        "duration_minutes": doc_input.duration_minutes,
        "supplemental_text": doc_input.supplemental_text,
        "story_state": story_state,
    }

    # --- Phase 2: YouTube research ---
    research_dir = run_dir / "research"
    if not resume or not (research_dir / "videos.json").exists():
        log("Phase 2 — Smart YouTube research (views-first ranking)")
        query, videos = rank_and_select_videos(
            seed_url=doc_input.youtube_url,
            topic=doc_input.topic,
            cfg=cfg.youtube,
        )
        save_research(research_dir, query=query, videos=videos)
    else:
        log("Phase 2 — reusing existing YouTube research")

    if research_only:
        log(f"Research-only complete: {research_dir}")
        return run_dir

    context["transcript_bundle"] = _build_transcript_bundle(research_dir)

    # --- Phase 3: Knowledge extraction ---
    kg_path = artifacts / "knowledge_graph.json"
    if not resume or not kg_path.exists() or from_phase == "extraction":
        log("Phase 3 — Knowledge extraction")
        result = KnowledgeExtractionAgent(cfg, client, run_dir).run(context)
        context["knowledge_graph"] = result["data"]
    else:
        context["knowledge_graph"] = _load_json(kg_path)

    # --- Phase 4: Timeline ---
    tl_path = artifacts / "timeline.json"
    if not resume or not tl_path.exists() or from_phase in ("extraction", "timeline"):
        log("Phase 4 — Timeline construction")
        result = TimelineAgent(cfg, client, run_dir).run(context)
        context["timeline"] = result["data"]
    else:
        context["timeline"] = _load_json(tl_path)

    # --- Phase 5: Character intelligence ---
    ch_path = artifacts / "character_profiles.json"
    if not resume or not ch_path.exists() or from_phase in ("extraction", "timeline", "characters"):
        log("Phase 5 — Character intelligence")
        result = CharacterIntelligenceAgent(cfg, client, run_dir).run(context)
        context["characters"] = result["data"]
    else:
        context["characters"] = _load_json(ch_path)

    # --- Progressive gap research ---
    gap_path = artifacts / "gap_research.json"
    if not resume or not gap_path.exists():
        log("Progressive research — gap filling via DeepSeek search")
        result = GapResearchAgent(cfg, client, run_dir).run(context)
        context["gap_research"] = result["data"]
        context["knowledge_graph"] = _merge_gap_facts(context["knowledge_graph"], result["data"])
        _save_json(kg_path, context["knowledge_graph"])
    else:
        context["gap_research"] = _load_json(gap_path)

    # --- Phase 6: Story architect ---
    outline_path = artifacts / "story_outline.json"
    if not resume or not outline_path.exists():
        log("Phase 6 — Story architecture")
        result = StoryArchitectAgent(cfg, client, run_dir).run(context)
        context["story_outline"] = result["data"]
    else:
        context["story_outline"] = _load_json(outline_path)

    # --- Fact verification ---
    fv_path = artifacts / "fact_verification.json"
    if not resume or not fv_path.exists():
        log("Fact verification")
        result = FactVerificationAgent(cfg, client, run_dir).run(context)
        context["fact_verification"] = result["data"]
    else:
        context["fact_verification"] = _load_json(fv_path)

    # --- Human checkpoint ---
    if cfg.pipeline.human_checkpoint and not skip_human_checkpoint:
        approved = run_dir / "checkpoints" / "APPROVED"
        if not approved.exists():
            _human_checkpoint(run_dir, context["fact_verification"], force=False)

    notes_file = run_dir / "checkpoints" / "human_review_notes.txt"
    context["human_review_notes"] = notes_file.read_text(encoding="utf-8").strip() if notes_file.exists() else ""

    # --- Phase 7: Script writer ---
    script_path = artifacts / "FULL_DOCUMENTARY_SCRIPT.txt"
    if not resume or not script_path.exists():
        log("Phase 7 — Documentary script writing")
        result = ScriptWriterAgent(cfg, client, run_dir).run(context)
        context["script_text"] = result["text"]
    else:
        context["script_text"] = script_path.read_text(encoding="utf-8")

    # --- Retention review ---
    rr_path = artifacts / "retention_report.json"
    if not resume or not rr_path.exists():
        log("Retention review")
        result = RetentionReviewerAgent(cfg, client, run_dir).run(context)
        context["retention_report"] = result["data"]
    else:
        context["retention_report"] = _load_json(rr_path)

    # --- Suggested visuals ---
    sv_path = artifacts / "suggested_visuals.json"
    if not resume or not sv_path.exists():
        log("Suggested visuals")
        result = VisualsAgent(cfg, client, run_dir).run(context)
        context["suggested_visuals"] = result["data"]
    else:
        context["suggested_visuals"] = _load_json(sv_path)

    # --- Final outputs bundle ---
    source_list = _build_source_list(context["knowledge_graph"], context["fact_verification"])
    _save_json(artifacts / "source_list_by_confidence.json", source_list)

    research_summary = {
        "topic": doc_input.topic,
        "input_type": doc_input.input_type,
        "youtube_url": doc_input.youtube_url,
        "duration_minutes": doc_input.duration_minutes,
        "target_characters": target_chars(doc_input.duration_minutes, cfg.pipeline.chars_per_minute),
        "research_videos": _load_json(research_dir / "videos.json") if (research_dir / "videos.json").exists() else [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": cfg.deepseek.model,
    }
    _save_json(artifacts / "research_summary.json", research_summary)

    # Update series continuity state
    outline = context.get("story_outline") or {}
    updated_state = {
        **story_state,
        "series_id": doc_input.series_id or cfg.pipeline.series_id or "",
        "revealed_facts": outline.get("revealed_facts") or story_state.get("revealed_facts", []),
        "withheld_facts_for_later": outline.get("withheld_facts_for_later") or [],
        "character_arc_state": outline.get("character_arc_state") or {},
        "open_threads": outline.get("open_threads") or [],
        "running_timeline_position": outline.get("running_timeline_position") or "",
    }
    _save_story_state(cfg.pipeline.storage_root, doc_input.series_id or cfg.pipeline.series_id, updated_state)
    _save_json(artifacts / "story_state.json", updated_state)

    # Copy key deliverables to output root for easy access
    deliverables = {
        "research_summary.json": artifacts / "research_summary.json",
        "knowledge_graph.json": kg_path,
        "timeline.json": tl_path,
        "character_profiles.json": ch_path,
        "story_outline.json": outline_path,
        "FULL_DOCUMENTARY_SCRIPT.txt": script_path,
        "retention_report.json": rr_path,
        "fact_verification.json": fv_path,
        "suggested_visuals.json": sv_path,
        "source_list_by_confidence.json": artifacts / "source_list_by_confidence.json",
    }
    for name, src in deliverables.items():
        if src.exists():
            (run_dir / name).write_bytes(src.read_bytes())

    log(f"Pipeline complete → {run_dir}")
    return run_dir
