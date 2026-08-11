"""Shared bullet-pointer story pipeline (CLI + Drupal worker)."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from library.fetch_youtube_transcript import extract_video_id, fetch_yt_metadata
from library import bullet_pointers as ptr
from library import story_generate as gen
from library import story_research as research


@dataclass
class StoryPipelineInput:
    seed_url: str
    related_urls: list[str]
    story_type: str
    duration_minutes: int
    folder_name: str | None = None
    research_dir_base: Path | None = None
    research_dir: Path | None = None
    languages: list[str] | None = None
    force: bool = False
    raw_transcripts: bool = False
    bullet_prompt_path: Path | None = None
    deepseek_config: Path | None = None
    prompt_path: Path | None = None
    extra_chars: int = 0
    target_chars_override: int | None = None
    # LLM
    llm_mode: str = "api"
    llm_model: str | None = None
    max_tokens: int = 64000
    timeout: int = 3600


@dataclass
class StoryPipelineResult:
    seed_title: str
    video_id: str
    slug: str
    research_dir: Path
    story_dir: Path
    story_text: str
    prompt: str
    raw_response: str
    source_chars: int
    target_chars: int
    video_count: int
    research_source: str
    prompt_file: Path
    bullet_flow: bool


def _use_bullet_pipeline(story_type: str, *, raw_transcripts: bool) -> bool:
    if raw_transcripts:
        return False
    return story_type in ("general", "crime", "god")


def run_story_pipeline(
    inp: StoryPipelineInput,
    *,
    skip_download: bool = False,
    research_only: bool = False,
    pointers_only: bool = False,
    prepare_only: bool = False,
    skip_llm: bool = False,
) -> StoryPipelineResult:
    """Download URLs → pointers → prompt → LLM → FULL_STORY.txt."""
    if len(inp.related_urls) < 1:
        raise ValueError("Need at least 2 YouTube URLs (seed + 1 source)")

    gen.load_dotenv()
    languages = inp.languages or ["hi", "en"]
    research_base = inp.research_dir_base or research.DEFAULT_RESEARCH_DIR
    video_id = extract_video_id(inp.seed_url)
    seed_meta = fetch_yt_metadata(video_id)
    seed_title = seed_meta.get("title") or video_id
    bullet_flow = _use_bullet_pipeline(inp.story_type, raw_transcripts=inp.raw_transcripts)

    if skip_download:
        if inp.research_dir is None:
            slug_hint = inp.folder_name or research.folder_slug_from_title(seed_title)
            research_dir = research_base / slug_hint
        else:
            research_dir = inp.research_dir
        if not research_dir.exists():
            raise FileNotFoundError(f"Research folder not found: {research_dir}")
    else:
        research_dir = research.run_research(
            inp.seed_url,
            output_base=research_base,
            folder_name=inp.folder_name,
            languages=languages,
            force=inp.force,
            explicit_related_urls=inp.related_urls,
        )

    videos = research.load_videos_json(research_dir / "videos.json")
    video_count = len([v for v in videos if v.get("video_id")])

    if research_only:
        return StoryPipelineResult(
            seed_title=seed_title,
            video_id=video_id,
            slug=gen.story_slug(seed_title),
            research_dir=research_dir,
            story_dir=research.story_output_dir(research_dir),
            story_text="",
            prompt="",
            raw_response="",
            source_chars=0,
            target_chars=0,
            video_count=video_count,
            research_source="transcripts",
            prompt_file=gen.V3_MASTER_PROMPT,
            bullet_flow=bullet_flow,
        )

    if bullet_flow:
        ptr.run_bullet_extraction(
            research_dir,
            topic=seed_title,
            bullet_prompt_path=inp.bullet_prompt_path,
            deepseek_config=inp.deepseek_config,
            force=inp.force,
        )
        if pointers_only:
            return StoryPipelineResult(
                seed_title=seed_title,
                video_id=video_id,
                slug=gen.story_slug(seed_title),
                research_dir=research_dir,
                story_dir=research.story_output_dir(research_dir),
                story_text="",
                prompt="",
                raw_response="",
                source_chars=0,
                target_chars=0,
                video_count=video_count,
                research_source="bullet_pointers",
                prompt_file=gen.V3_MASTER_PROMPT,
                bullet_flow=True,
            )
        source_text, source_chars = ptr.pointer_source_for_prompt(research_dir)
        research_source = "bullet_pointers"
    else:
        source_text, source_chars, used_videos = research.combine_transcripts(
            research_dir, max_related=None
        )
        video_count = len(used_videos)
        research_source = "transcripts"

    target_chars = gen.compute_target_chars(
        inp.story_type,
        source_chars,
        video_count,
        duration_minutes=inp.duration_minutes,
        extra_chars=inp.extra_chars,
        target_override=inp.target_chars_override,
    )
    slug = gen.story_slug(seed_title)
    prompt_file = (
        inp.prompt_path
        if inp.prompt_path
        else gen.default_prompt_for_pipeline(
            use_bullet_pointers=bullet_flow, story_type=inp.story_type
        )
    )

    if bullet_flow and prompt_file == gen.V3_MASTER_PROMPT:
        prompt = gen.build_v3_prompt_from_pointers(
            prompt_file,
            source_text,
            target_chars,
            duration_minutes=inp.duration_minutes,
            topic=seed_title,
            story_type=inp.story_type,
        )
    else:
        prompt = gen.build_prompt_for_type(
            inp.story_type,
            prompt_file,
            source_text,
            target_chars,
            duration_minutes=inp.duration_minutes,
        )

    story_dir = research.story_output_dir(research_dir)

    if prepare_only:
        story_dir.mkdir(parents=True, exist_ok=True)
        (story_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        pointers_out = research_dir / ptr.COMBINED_FILENAME
        if bullet_flow and pointers_out.is_file():
            shutil.copy2(pointers_out, story_dir / ptr.COMBINED_FILENAME)
        return StoryPipelineResult(
            seed_title=seed_title,
            video_id=video_id,
            slug=slug,
            research_dir=research_dir,
            story_dir=story_dir,
            story_text="",
            prompt=prompt,
            raw_response="",
            source_chars=source_chars,
            target_chars=target_chars,
            video_count=video_count,
            research_source=research_source,
            prompt_file=prompt_file,
            bullet_flow=bullet_flow,
        )

    if skip_llm:
        raw_response = ""
        story_text = ""
    else:
        model = inp.llm_model or "claude-sonnet-4-20250514"
        raw_response = gen.call_llm(
            prompt,
            provider="claude",
            mode=inp.llm_mode,
            model=model,
            max_tokens=inp.max_tokens,
            browser="cdp",
            firefox_profile=gen.DEFAULT_FIREFOX_PROFILE,
            cdp_url=None,
            timeout=inp.timeout,
            claude_code_model=None,
        )
        story_text = gen.extract_full_script(raw_response)

    gen.save_pipeline_outputs(
        story_dir,
        slug=slug,
        title=seed_title,
        video_id=video_id,
        youtube_url=inp.seed_url,
        story_type=inp.story_type,
        research_dir=research_dir,
        source_chars=source_chars,
        target_chars=target_chars,
        prompt=prompt,
        raw_response=raw_response,
        story_text=story_text,
        video_count=video_count,
        duration_minutes=inp.duration_minutes,
        prompt_file=prompt_file,
        research_source=research_source,
    )

    return StoryPipelineResult(
        seed_title=seed_title,
        video_id=video_id,
        slug=slug,
        research_dir=research_dir,
        story_dir=story_dir,
        story_text=story_text,
        prompt=prompt,
        raw_response=raw_response,
        source_chars=source_chars,
        target_chars=target_chars,
        video_count=video_count,
        research_source=research_source,
        prompt_file=prompt_file,
        bullet_flow=bullet_flow,
    )
