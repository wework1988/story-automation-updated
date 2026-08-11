from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent


class StoryArchitectAgent(BaseAgent):
    name = "story_architect"
    output_filename = "story_outline.json"
    prompt_file = "story_architect.txt"
    max_tokens_key = "architect"

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        return template.format(
            topic=context["topic"],
            duration_minutes=context["duration_minutes"],
            knowledge_graph=json.dumps(context["knowledge_graph"], ensure_ascii=False)[:60_000],
            timeline=json.dumps(context["timeline"], ensure_ascii=False)[:40_000],
            characters=json.dumps(context["characters"], ensure_ascii=False)[:40_000],
            gap_research=json.dumps(context.get("gap_research", {}), ensure_ascii=False)[:20_000],
            story_state=json.dumps(context.get("story_state", {}), ensure_ascii=False),
        )
