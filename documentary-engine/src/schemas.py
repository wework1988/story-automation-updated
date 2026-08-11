"""JSON schemas and helpers for inter-agent structured data."""

from __future__ import annotations

import json
import re
from typing import Any


EDITORIAL_RULES = """
Editorial style:
- Cinematic storytelling, documentary pacing, suspense-driven narrative
- Character-driven, investigative journalism style
- Indian audience first — explain from Indian context when relevant
- Simple Hindi narration — clarity over academic writing
- Never feel like Wikipedia; feel like Netflix

Framing rule:
- Give India's institutions, security forces, and key figures fair, specific credit where the record supports it
- Avoid cynical or foreign-outsider framing by default
- Do NOT suppress documented failures, controversies, or criticism
- Where sources disagree, present as disagreement — do not pick sides arbitrarily
- Never invent evidence; acknowledge uncertainty when needed

Transcript rule:
- YouTube transcripts are RESEARCH LEADS to verify — not reusable narration
- Extract facts and structure in your own words
"""

DISCLAIMER_HINDI = (
    "यह डॉक्यूमेंट्री सार्वजनिक रूप से उपलब्ध स्रोतों — समाचार रिपोर्ट, किताबें, "
    "साक्षात्कार, डॉक्यूमेंट्री, शोध सामग्री, और जहाँ उपलब्ध हो आधिकारिक जानकारी — "
    "पर आधारित है। कुछ दृश्यों में कहानी को स्पष्ट करने के लिए सिनेमाई या "
    "नाटकीय प्रस्तुति का उपयोग किया गया हो सकता है। ऐसा कोई भी नाटकीकरण केवल "
    "वर्णन में सहायता के लिए है और साक्ष्य के समर्थन में न हो तो वास्तविक "
    "पुनर्निर्माण के रूप में नहीं लिया जाना चाहिए।"
)


def target_chars(duration_minutes: int, chars_per_minute: int = 1000) -> int:
    return duration_minutes * chars_per_minute


def empty_story_state(series_id: str | None = None) -> dict[str, Any]:
    return {
        "series_id": series_id or "",
        "revealed_facts": [],
        "withheld_facts_for_later": [],
        "character_arc_state": {},
        "open_threads": [],
        "running_timeline_position": "",
    }


def extract_json_block(text: str) -> Any:
    """Parse JSON from model output — raw JSON or fenced code block."""
    text = text.strip()
    if not text:
        raise ValueError("Empty model response")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if fence:
        return json.loads(fence.group(1).strip())

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])

    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])

    raise ValueError("Could not parse JSON from model response")


def slugify(text: str, max_len: int = 60) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    slug = text.strip("-") or "documentary"
    return slug[:max_len]
