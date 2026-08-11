from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent


class GapResearchAgent(BaseAgent):
    name = "gap_research"
    output_filename = "gap_research.json"
    prompt_file = "gap_research.txt"
    max_tokens_key = "gap_research"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        gaps = context.get("knowledge_graph", {}).get("unknown_questions", [])
        if not gaps:
            empty = {"gaps_identified": [], "new_facts": [], "searches_performed": []}
            out = self.run_dir / "artifacts" / self.output_filename
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(empty, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"data": empty, "finish_reason": "skipped"}
        return super().run(context)

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        knowledge = json.dumps(context["knowledge_graph"], ensure_ascii=False, indent=2)
        return template.format(topic=context["topic"], knowledge_graph=knowledge[:80_000])
