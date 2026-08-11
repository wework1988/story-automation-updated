from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent


class VisualsAgent(BaseAgent):
    name = "suggested_visuals"
    output_filename = "suggested_visuals.json"
    prompt_file = "suggested_visuals.txt"
    max_tokens_key = "architect"

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        return template.format(
            topic=context["topic"],
            story_outline=json.dumps(context.get("story_outline", {}), ensure_ascii=False)[:40_000],
            script=(context.get("script_text") or "")[:60_000],
        )
