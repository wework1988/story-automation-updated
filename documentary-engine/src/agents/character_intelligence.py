from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent


class CharacterIntelligenceAgent(BaseAgent):
    name = "character_intelligence"
    output_filename = "character_profiles.json"
    prompt_file = "character_intelligence.txt"
    max_tokens_key = "characters"

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        knowledge = json.dumps(context["knowledge_graph"], ensure_ascii=False, indent=2)
        timeline = json.dumps(context["timeline"], ensure_ascii=False, indent=2)
        return template.format(
            topic=context["topic"],
            knowledge_graph=knowledge[:80_000],
            timeline=timeline[:40_000],
        )
