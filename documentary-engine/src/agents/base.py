"""Base agent utilities."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..config import EngineConfig
from ..deepseek_client import DeepSeekClient
from ..schemas import EDITORIAL_RULES, extract_json_block


class BaseAgent(ABC):
    name: str = "base"
    output_filename: str = "output.json"
    text_output_filename: str | None = None
    prompt_file: str = ""
    max_tokens_key: str = "extraction"
    json_mode: bool = True

    def __init__(self, cfg: EngineConfig, client: DeepSeekClient, run_dir: Path) -> None:
        self.cfg = cfg
        self.client = client
        self.run_dir = run_dir
        self.prompts_dir = Path(__file__).resolve().parents[2] / "prompts"

    def load_prompt(self) -> str:
        path = self.prompts_dir / self.prompt_file
        if not path.exists():
            raise FileNotFoundError(f"Prompt not found: {path}")
        return path.read_text(encoding="utf-8").strip()

    def system_prompt(self) -> str:
        return (
            "You are an expert documentary research and screenplay agent.\n"
            "Respond with highest quality, investigative rigor, and cinematic storytelling awareness.\n"
            f"{EDITORIAL_RULES}"
        )

    @abstractmethod
    def build_user_prompt(self, context: dict[str, Any]) -> str:
        ...

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        user_prompt = self.build_user_prompt(context)
        prompt_dump = self.run_dir / "prompts" / f"{self.name}.prompt.txt"
        prompt_dump.parent.mkdir(parents=True, exist_ok=True)
        prompt_dump.write_text(user_prompt, encoding="utf-8")

        max_tokens = self.cfg.deepseek.max_tokens[self.max_tokens_key]
        raw, finish = self.client.chat(
            system_prompt=self.system_prompt(),
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            label=self.name,
        )

        out_dir = self.run_dir / "artifacts"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{self.name}.raw.txt").write_text(raw, encoding="utf-8")

        result: dict[str, Any]
        if self.json_mode:
            parsed = extract_json_block(raw)
            (out_dir / self.output_filename).write_text(
                json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            result = {"data": parsed, "finish_reason": finish}
        else:
            text_path = out_dir / (self.text_output_filename or f"{self.name}.txt")
            text_path.write_text(raw, encoding="utf-8")
            result = {"text": raw, "path": str(text_path), "finish_reason": finish}

        return result
