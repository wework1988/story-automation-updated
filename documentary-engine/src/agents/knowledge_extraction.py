from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent


class KnowledgeExtractionAgent(BaseAgent):
    name = "knowledge_extraction"
    output_filename = "knowledge_graph.json"
    prompt_file = "knowledge_extraction.txt"
    max_tokens_key = "extraction"

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        transcripts = context.get("transcript_bundle", "")
        supplemental = context.get("supplemental_text", "")
        topic = context["topic"]
        return template.format(
            topic=topic,
            transcripts=transcripts[:120_000],
            supplemental=supplemental[:20_000] or "(none)",
        )
