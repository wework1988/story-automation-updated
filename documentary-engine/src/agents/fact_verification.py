from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent


class FactVerificationAgent(BaseAgent):
    name = "fact_verification"
    output_filename = "fact_verification.json"
    prompt_file = "fact_verification.txt"
    max_tokens_key = "verification"

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        return template.format(
            topic=context["topic"],
            knowledge_graph=json.dumps(context["knowledge_graph"], ensure_ascii=False)[:80_000],
            gap_research=json.dumps(context.get("gap_research", {}), ensure_ascii=False)[:30_000],
            story_outline=json.dumps(context.get("story_outline", {}), ensure_ascii=False)[:40_000],
        )
