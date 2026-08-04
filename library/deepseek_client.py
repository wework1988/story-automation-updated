"""Minimal DeepSeek API client for story-agent bullet extraction."""

from __future__ import annotations

import errno
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "documentary-engine" / "deepseek.config.ini"


def log(msg: str) -> None:
    print(f"[deepseek] {msg}", flush=True)


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
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


@dataclass(frozen=True)
class DeepSeekSettings:
    api_key: str
    base_url: str
    model: str
    temperature: float
    thinking: bool
    reasoning_effort: str
    api_max_retries: int
    max_tokens_bullets: int


def load_deepseek_settings(config_path: Path | None = None) -> DeepSeekSettings:
    import configparser

    _load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set. Add it to repo-root .env")

    path = config_path or Path(os.environ.get("DEEPSEEK_CONFIG", str(DEFAULT_CONFIG)))
    base_url = "https://api.deepseek.com"
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro").strip()
    temperature = 0.3
    thinking = False
    reasoning_effort = "high"
    api_max_retries = 10
    max_tokens_bullets = 16384

    if path.exists():
        cp = configparser.ConfigParser()
        cp.read(path, encoding="utf-8")
        if "deepseek_connection" in cp:
            ds = cp["deepseek_connection"]
            base_url = ds.get("base_url", base_url).strip()
            model = os.environ.get("DEEPSEEK_MODEL", ds.get("model", model)).strip()
            temperature = float(ds.get("temperature", str(temperature)))
            api_max_retries = int(ds.get("api_max_retries", str(api_max_retries)))
        if "thinking" in cp:
            th = cp["thinking"]
            thinking = _bool(os.environ.get("DEEPSEEK_THINKING"), _bool(th.get("enabled"), thinking))
            reasoning_effort = os.environ.get(
                "DEEPSEEK_REASONING_EFFORT", th.get("reasoning_effort", reasoning_effort)
            ).strip()
        if "token_budget" in cp:
            tb = cp["token_budget"]
            max_tokens_bullets = int(
                os.environ.get(
                    "DEEPSEEK_MAX_TOKENS_BULLETS",
                    tb.get("max_tokens_extraction", str(max_tokens_bullets)),
                )
            )

    return DeepSeekSettings(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        thinking=thinking,
        reasoning_effort=reasoning_effort,
        api_max_retries=api_max_retries,
        max_tokens_bullets=max_tokens_bullets,
    )


def _retryable(exc: BaseException) -> bool:
    errno_reset = {
        getattr(errno, "ECONNRESET", -1),
        getattr(errno, "EPIPE", -1),
        getattr(errno, "ETIMEDOUT", -1),
        getattr(errno, "ECONNABORTED", -1),
        54,
        104,
        10054,
    }
    errno_reset = {x for x in errno_reset if isinstance(x, int) and x >= 0}
    cur: BaseException | None = exc
    while cur is not None:
        if isinstance(cur, (TimeoutError, ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
            return True
        if isinstance(cur, OSError) and getattr(cur, "errno", None) in errno_reset:
            return True
        try:
            import httpx

            if isinstance(
                cur,
                (
                    httpx.ReadError,
                    httpx.ConnectError,
                    httpx.RemoteProtocolError,
                    httpx.ReadTimeout,
                    httpx.WriteTimeout,
                    httpx.ConnectTimeout,
                ),
            ):
                return True
        except ImportError:
            pass
        cur = cur.__cause__
    return False


def _backoff(attempt: int, base: float = 8.0, cap: float = 120.0) -> float:
    return min(cap, base * float(2**attempt))


class DeepSeekClient:
    def __init__(self, settings: DeepSeekSettings) -> None:
        self.settings = settings
        from openai import OpenAI

        self._client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        label: str,
        temperature: float | None = None,
        thinking: bool | None = None,
    ) -> str:
        cfg = self.settings
        use_thinking = cfg.thinking if thinking is None else thinking
        legacy_reasoner = "reasoner" in cfg.model.lower()
        thinking_effective = use_thinking and not legacy_reasoner

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        kwargs: dict[str, Any] = {
            "model": cfg.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        temp = cfg.temperature if temperature is None else temperature
        if legacy_reasoner or not thinking_effective:
            kwargs["temperature"] = temp
        if thinking_effective and cfg.reasoning_effort:
            kwargs["reasoning_effort"] = cfg.reasoning_effort
        if thinking_effective:
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

        create_fn: Callable[..., Any] = self._client.chat.completions.create
        max_tries = max(1, cfg.api_max_retries)

        for attempt in range(max_tries):
            try:
                t0 = time.time()
                log(f"[{label}] calling {cfg.model} (max_tokens={max_tokens})…")
                resp = create_fn(**kwargs)
                dt = time.time() - t0
                choice = resp.choices[0]
                content = (choice.message.content or "").strip()
                finish = getattr(choice, "finish_reason", None)
                log(f"[{label}] done in {dt:.1f}s finish={finish}")
                if finish == "length":
                    log(f"[{label}] WARNING: output may be truncated (max_tokens)")
                if not content:
                    raise RuntimeError(f"[{label}] empty response from DeepSeek")
                return content
            except Exception as exc:
                if attempt + 1 >= max_tries or not _retryable(exc):
                    raise
                pause = _backoff(attempt)
                log(f"[{label}] retry after {type(exc).__name__} — sleep {pause:.1f}s")
                time.sleep(pause)
        raise RuntimeError("unreachable")
