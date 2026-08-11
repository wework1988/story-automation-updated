from __future__ import annotations

import json
from typing import Any

from .base import BaseAgent


class RetentionReviewerAgent(BaseAgent):
    name = "retention_reviewer"
    output_filename = "retention_report.json"
    prompt_file = "retention_reviewer.txt"
    max_tokens_key = "retention"

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.load_prompt()
        script = context.get("script_text", "")
        return template.format(
            topic=context["topic"],
            duration_minutes=context["duration_minutes"],
            script=script[:80_000],
        )
