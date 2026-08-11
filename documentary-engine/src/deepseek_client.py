"""Standalone DeepSeek API client — expert quality settings."""

from __future__ import annotations

import errno
import time
from typing import Any, Callable

from .config import DeepSeekConfig


def log(msg: str) -> None:
    print(f"[documentary-engine] {msg}", flush=True)


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
        try:
            import openai

            for cls in (
                getattr(openai, "APIConnectionError", None),
                getattr(openai, "APITimeoutError", None),
            ):
                if cls and isinstance(cur, cls):
                    return True
        except ImportError:
            pass
        cur = cur.__cause__
    return False


def _backoff(attempt: int, base: float = 8.0, cap: float = 120.0) -> float:
    return min(cap, base * float(2**attempt))


def _extra_body(cfg: DeepSeekConfig, *, enable_search: bool | None = None) -> dict[str, Any]:
    eb: dict[str, Any] = {}
    search = cfg.enable_search if enable_search is None else enable_search
    if search:
        eb["search"] = {"type": cfg.search_type}
    legacy_reasoner = "reasoner" in cfg.model.lower()
    if cfg.thinking and not legacy_reasoner:
        eb["thinking"] = {"type": "enabled"}
    return eb


class DeepSeekClient:
    def __init__(self, cfg: DeepSeekConfig) -> None:
        self.cfg = cfg
        from openai import OpenAI

        self._client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        label: str,
        temperature: float | None = None,
        enable_search: bool | None = None,
    ) -> tuple[str, str | None]:
        cfg = self.cfg
        legacy_reasoner = "reasoner" in cfg.model.lower()
        thinking_effective = cfg.thinking and not legacy_reasoner

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

        extra = _extra_body(cfg, enable_search=enable_search)
        if extra:
            kwargs["extra_body"] = extra

        create_fn: Callable[..., Any] = self._client.chat.completions.create
        max_tries = max(1, cfg.api_max_retries)

        for attempt in range(max_tries):
            try:
                t0 = time.time()
                log(f"[{label}] calling DeepSeek ({cfg.model}, max_tokens={max_tokens})…")
                resp = create_fn(**kwargs)
                dt = time.time() - t0
                choice = resp.choices[0]
                content = (choice.message.content or "").strip()
                finish = getattr(choice, "finish_reason", None)
                usage = getattr(resp, "usage", None)
                if usage:
                    log(
                        f"[{label}] done in {dt:.1f}s — "
                        f"tokens in≈{getattr(usage, 'prompt_tokens', '?')} "
                        f"out≈{getattr(usage, 'completion_tokens', '?')} "
                        f"finish={finish}"
                    )
                else:
                    log(f"[{label}] done in {dt:.1f}s finish={finish}")
                if finish == "length":
                    log(f"[{label}] WARNING: output hit max_tokens — may be truncated")
                if not content:
                    raise RuntimeError(f"[{label}] empty response from DeepSeek")
                return content, finish
            except Exception as exc:
                if attempt + 1 >= max_tries or not _retryable(exc):
                    raise
                pause = _backoff(attempt)
                log(f"[{label}] retry {attempt + 2}/{max_tries} after {type(exc).__name__} — sleep {pause:.1f}s")
                time.sleep(pause)

        raise RuntimeError("unreachable")
