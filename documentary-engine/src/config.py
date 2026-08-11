"""Documentary Engine — standalone configuration loader."""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ENGINE_ROOT / "deepseek.config.ini"
DEFAULT_STORAGE = ENGINE_ROOT / "storage"
PROMPTS_DIR = ENGINE_ROOT / "prompts"


def _load_dotenv() -> None:
    env_path = ENGINE_ROOT.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _int(val: str | None, default: int) -> int:
    try:
        return int((val or "").strip())
    except ValueError:
        return default


def _float(val: str | None, default: float) -> float:
    try:
        return float((val or "").strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float
    thinking: bool
    reasoning_effort: str
    enable_search: bool
    search_type: str
    api_max_retries: int
    max_tokens: dict[str, int]


@dataclass(frozen=True)
class YouTubeResearchConfig:
    candidate_limit: int
    select_count: int
    min_views: int
    min_engagement_rate: float
    min_duration_seconds: int


@dataclass(frozen=True)
class PipelineConfig:
    duration_minutes: int
    chars_per_minute: int
    human_checkpoint: bool
    series_id: str | None
    language: str
    include_disclaimer: bool
    storage_root: Path


@dataclass(frozen=True)
class EngineConfig:
    deepseek: DeepSeekConfig
    youtube: YouTubeResearchConfig
    pipeline: PipelineConfig


def resolve_api_key() -> str:
    for key in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    raise RuntimeError(
        "DEEPSEEK_API_KEY not set. Add it to repo-root .env or export it in your shell."
    )


def load_config(config_path: Path | None = None) -> EngineConfig:
    _load_dotenv()
    path = config_path or Path(os.environ.get("DOCUMENTARY_CONFIG", str(DEFAULT_CONFIG)))
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    cp = configparser.ConfigParser()
    cp.read(path, encoding="utf-8")

    def sec(name: str) -> configparser.SectionProxy:
        return cp[name]

    ds = sec("deepseek_connection")
    th = sec("thinking")
    ss = sec("smart_search")
    tb = sec("token_budget")
    yt = sec("youtube_research")
    pl = sec("pipeline")
    ed = sec("editorial")

    storage = Path(os.environ.get("DOCUMENTARY_STORAGE", str(DEFAULT_STORAGE)))

    deepseek = DeepSeekConfig(
        api_key=resolve_api_key(),
        base_url=ds.get("base_url", "https://api.deepseek.com").strip(),
        model=os.environ.get("DEEPSEEK_MODEL", ds.get("model", "deepseek-v4-pro")).strip(),
        temperature=_float(os.environ.get("DEEPSEEK_TEMPERATURE"), _float(ds.get("temperature"), 0.3)),
        thinking=_bool(os.environ.get("DEEPSEEK_THINKING"), _bool(th.get("enabled"), True)),
        reasoning_effort=os.environ.get(
            "DEEPSEEK_REASONING_EFFORT", th.get("reasoning_effort", "high")
        ).strip(),
        enable_search=_bool(os.environ.get("DEEPSEEK_ENABLE_SEARCH"), _bool(ss.get("internet_enabled"), True)),
        search_type=os.environ.get("DEEPSEEK_SEARCH_TYPE", ss.get("search_type", "web")).strip(),
        api_max_retries=_int(os.environ.get("DEEPSEEK_API_MAX_RETRIES"), _int(ds.get("api_max_retries"), 10)),
        max_tokens={
            "research": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_RESEARCH"), _int(tb.get("max_tokens_research"), 65536)),
            "extraction": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_EXTRACTION"), _int(tb.get("max_tokens_extraction"), 65536)),
            "timeline": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_TIMELINE"), _int(tb.get("max_tokens_timeline"), 32768)),
            "characters": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_CHARACTERS"), _int(tb.get("max_tokens_characters"), 32768)),
            "architect": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_ARCHITECT"), _int(tb.get("max_tokens_architect"), 32768)),
            "script": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_SCRIPT"), _int(tb.get("max_tokens_script"), 65536)),
            "retention": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_RETENTION"), _int(tb.get("max_tokens_retention"), 32768)),
            "verification": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_VERIFICATION"), _int(tb.get("max_tokens_verification"), 32768)),
            "gap_research": _int(os.environ.get("DEEPSEEK_MAX_TOKENS_GAP"), _int(tb.get("max_tokens_gap_research"), 32768)),
        },
    )

    youtube = YouTubeResearchConfig(
        candidate_limit=_int(yt.get("candidate_limit"), 20),
        select_count=_int(yt.get("select_count"), 4),
        min_views=_int(yt.get("min_views"), 50_000),
        min_engagement_rate=_float(yt.get("min_engagement_rate"), 0.002),
        min_duration_seconds=_int(yt.get("min_duration_seconds"), 300),
    )

    series_id = os.environ.get("DOCUMENTARY_SERIES_ID", pl.get("series_id", "")).strip() or None

    pipeline = PipelineConfig(
        duration_minutes=_int(os.environ.get("DOCUMENTARY_DURATION"), _int(pl.get("duration_minutes"), 30)),
        chars_per_minute=_int(pl.get("chars_per_minute"), 1000),
        human_checkpoint=_bool(os.environ.get("DOCUMENTARY_HUMAN_CHECKPOINT"), _bool(pl.get("human_checkpoint"), True)),
        series_id=series_id,
        language=ed.get("language", "hindi").strip(),
        include_disclaimer=_bool(ed.get("disclaimer"), True),
        storage_root=storage,
    )

    return EngineConfig(deepseek=deepseek, youtube=youtube, pipeline=pipeline)
