from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent


class TimelineAgent(BaseAgent):
    name = "timeline"
    output_filename = "timeline.json"
    prompt_file = "timeline.txt"
    max_tokens_key = "timeline"

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        knowledge = json.dumps(context["knowledge_graph"], ensure_ascii=False, indent=2)
        return template.format(topic=context["topic"], knowledge_graph=knowledge[:100_000])
