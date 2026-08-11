from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent
from ..schemas import DISCLAIMER_HINDI, target_chars


class ScriptWriterAgent(BaseAgent):
    name = "script_writer"
    text_output_filename = "FULL_DOCUMENTARY_SCRIPT.txt"
    prompt_file = "script_writer.txt"
    max_tokens_key = "script"
    json_mode = False

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        chars = target_chars(context["duration_minutes"], self.cfg.pipeline.chars_per_minute)
        verification = context.get("fact_verification", {})
        human_notes = context.get("human_review_notes", "")
        disclaimer = DISCLAIMER_HINDI if self.cfg.pipeline.include_disclaimer else ""

        return template.format(
            topic=context["topic"],
            duration_minutes=context["duration_minutes"],
            target_chars=chars,
            story_outline=json.dumps(context["story_outline"], ensure_ascii=False)[:50_000],
            timeline=json.dumps(context["timeline"], ensure_ascii=False)[:30_000],
            characters=json.dumps(context["characters"], ensure_ascii=False)[:30_000],
            fact_verification=json.dumps(verification, ensure_ascii=False)[:40_000],
            human_review_notes=human_notes or "(none — approved)",
            disclaimer=disclaimer,
        )
