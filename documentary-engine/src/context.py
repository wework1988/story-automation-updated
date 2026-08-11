"""Seed-transcript context → content-aware YouTube search (any story type).

Pipeline (generic — not hardcoded to one topic):
  1. Download the seed transcript first.
  2. Extract PRIMARY (who/what) + ANCHORS (what makes this telling specific)
     from the seed title + transcript — never from broad SEO tags alone.
  3. Search priority channels with "primary + anchor" queries.
  4. Keep a candidate only if it hits the primary AND shares enough seed
     anchors (same story), not merely the same country/genre.

Broad tags like "Iran Nuclear Program" / "True Crime" are rejected as queries
because they match every video in a niche. Event-verb hints (track, murder,
escape…) only boost anchors when the seed itself uses them.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

# Excludes danda (U+0964), double danda (U+0965) and abbreviation sign (U+0970),
# which otherwise get glued onto the end of Hindi words.
DEVANAGARI_RANGE = "\u0900-\u0963\u0966-\u096f\u0971-\u097f"
DEVANAGARI_CHAR_RE = re.compile(rf"[{DEVANAGARI_RANGE}]")

TOKEN_RE = re.compile(rf"[A-Za-z{DEVANAGARI_RANGE}][A-Za-z0-9{DEVANAGARI_RANGE}'\-]*")
CAPITAL_RUN_RE = re.compile(r"\b[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]{2,}){0,2}\b")
NUMBER_RE = re.compile(r"\b\d[\d,.]*\b")
CAPTION_MARKER_RE = re.compile(r"[\[(](?:[^\])]{0,40})[\])]")
URL_RE = re.compile(r"https?://\S+")

ENGLISH_STOPWORDS = {
    "the", "and", "for", "are", "was", "were", "this", "that", "with", "from",
    "have", "has", "had", "but", "not", "you", "your", "they", "them", "their",
    "will", "would", "could", "should", "can", "his", "her", "him", "she", "who",
    "what", "when", "where", "why", "how", "which", "into", "than", "then",
    "there", "here", "been", "being", "does", "did", "doing", "just", "also",
    "very", "more", "most", "some", "such", "only", "over", "under", "after",
    "before", "about", "because", "while", "these", "those", "each", "other",
    "video", "channel", "subscribe", "explained", "full", "story", "part",
    "episode", "watch", "today", "know", "like", "back", "even", "still",
    "well", "much", "many", "made", "make", "take", "come", "went", "said",
    "one", "two", "now", "new", "out", "get", "got", "see", "way", "day",
    "news", "latest", "update", "updates", "live", "viral", "trending", "shorts",
    "documentary", "podcast", "hindi", "english", "educational", "explainer",
    "inside", "real", "truth", "facts",
    "music", "time", "things", "thing", "street", "click", "share", "comment",
    "amazon", "google", "apple", "garner", "intel",  # common caption false-positives
    # NOTE: do NOT stopword track/kill/assassinate — those are story-angle words.
}

HINDI_STOPWORDS = {
    "के", "का", "की", "को", "में", "से", "है", "हैं", "था", "थी", "थे", "और",
    "पर", "यह", "वह", "ये", "वो", "कि", "ने", "तो", "भी", "एक", "कर", "किया",
    "करने", "करते", "करता", "करती", "लिए", "नहीं", "हो", "हुआ", "हुई", "हुए",
    "गया", "गई", "गए", "अपने", "अपनी", "इस", "उस", "जो", "कोई", "सब", "बहुत",
    "अब", "फिर", "क्या", "कैसे", "क्यों", "जब", "तक", "ही", "या", "साथ", "बाद",
    "पहले", "दिया", "देने", "रहा", "रही", "रहे", "होता", "होती", "होते", "होने",
    "कुछ", "मैं", "आप", "हम", "उन", "इन", "बात", "तरह", "दो", "जिस",
    "जिसका", "जिसकी", "जिसके", "उसका", "उसकी", "उसके", "इसका", "इसकी", "इसके",
    "सकता", "सकती", "सकते", "चाहिए", "लेकिन", "अगर", "जैसे", "वहां", "यहां",
    "दोस्तों", "वीडियो", "चैनल", "सब्सक्राइब", "नमस्कार", "स्वागत", "आज",
    "आपको", "आपके", "आपकी", "मेरे", "हमारे", "बिल्कुल", "सिर्फ", "साल",
    "पूरी", "पूरा", "पूरे", "कहानी", "वाले", "वाला", "वाली", "बीच", "जाता",
    "जाती", "जाते", "देखिए", "समझिए", "यानी", "मतलब", "दरअसल", "संगीत",
    "म्यूजिक", "टाइम", "सारी", "सारा", "सारे", "अंदर", "बाहर", "चीज", "चीजें",
    "चीजों", "ऊपर", "नीचे", "लोग", "लोगों", "यहाँ", "वहाँ", "इसे", "उसे",
    "इनके", "इनका", "इनकी", "उनका", "उनकी", "उन्हें", "उन्होंने", "इन्हें",
    "ऐसे", "ऐसा", "ऐसी", "वैसे", "जिन", "जिन्हें", "कहा", "कहते", "कहना",
    "मिल", "मिला", "मिली", "गई।", "जाए", "जाएगा", "जाएगी", "रखा", "लगा",
    "लगी", "लगे", "आया", "आई", "आए", "दिन", "रात", "जगह", "काम", "नाम",
    "शुरू", "खत्म", "देश", "दुनिया", "जान", "तैयार", "मामला", "मामले",
    # Auto-caption filler / packaging — never topic subjects
    "स्ट्रीट", "म्यूजिक", "म्यूज़िक", "क्लिक", "लाइक", "शेयर", "कमेंट",
    "वॉच", "देखो", "सुनो", "बताते", "बताऊंगा", "बताऊँगा", "चलिए", "आगे",
    "पीछे", "यही", "वही", "बाकी", "बाक़ी", "पूरी", "थोड़ी", "ज्यादा",
    # Generic verbs / fillers that polluted subjects for story 123
    "करके", "सबसे", "करना", "एरिया", "स्टार्ट", "इतना", "उनको", "क्योंकि",
}

STOPWORDS = ENGLISH_STOPWORDS | HINDI_STOPWORDS

# Category / region bucket words — alone they match half of YouTube in that niche.
# A tag made only of these is too broad for related-video search (any story type).
BROAD_TOPIC_WORDS = {
    # Geopolitics / news packaging
    "iran", "israel", "usa", "america", "american", "us", "war", "news",
    "deal", "program", "programme", "nuclear", "politics", "middle", "east",
    "world", "india", "indian", "pakistan", "china", "russia", "ukraine",
    "ईरान", "इजराइल", "अमेरिका", "न्यूक्लियर", "जंग", "युद्ध", "समाचार",
    "डील", "प्रोग्राम", "दुनिया", "भारत", "पाकिस्तान", "चीन", "रूस",
    # Genre packaging (never the specific story)
    "crime", "scam", "mystery", "history", "documentary", "explained",
    "latest", "breaking", "update", "viral", "shorts", "podcast",
    "क्राइम", "घोटाला", "रहस्य", "इतिहास", "दस्तावेज़ी",
}

# Optional verb hints — when these appear in the *seed title/transcript*, they
# become anchors. They are NOT required for relevance on other story types.
EVENT_VERB_HINTS = {
    "track", "tracked", "tracking", "kill", "killed", "killing", "assassin",
    "assassinate", "assassination", "eliminate", "eliminated", "elimination",
    "strike", "struck", "escape", "escaped", "kidnap", "kidnapped", "rob",
    "robbed", "scam", "scammed", "fraud", "murder", "murdered", "arrest",
    "arrested", "capture", "captured", "hack", "hacked", "infiltrate",
    "हत्या", "मारा", "मारने", "मारे", "मारना", "ट्रैक", "ट्रैकिंग",
    "फरार", "अपहरण", "लूट", "घोटाला", "हैक", "घुसपैठ", "गिरफ्तार",
}

# Structural words from our own research file headers — never topic entities.
ENTITY_BLOCKLIST = {
    "source", "url", "upload", "uploads", "views", "channel", "topic",
    "research", "material", "sources", "transcript", "youtube", "subscribe",
    "key subjects", "topic match",
}

# Words that describe the packaging of a video, never its subject.
TITLE_NOISE_RE = re.compile(
    r"\b(full\s+video|part\s*\d+|episode\s*\d+|ep\s*\d+|hindi|english|"
    r"documentary|explained|kissa|podcast|ft\.?|feat\.?)\b",
    re.IGNORECASE,
)

DEV_TO_LATIN = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "n",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v", "ळ": "l",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "क़": "k", "ख़": "kh", "ग़": "g", "ज़": "z", "ड़": "r", "ढ़": "rh", "फ़": "f",
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ii", "उ": "u", "ऊ": "uu",
    "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au", "ऑ": "o", "ऍ": "e",
    "ा": "aa", "ि": "i", "ी": "ii", "ु": "u", "ू": "uu", "ृ": "ri",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ॉ": "o", "ॅ": "e",
    "ं": "n", "ँ": "n", "ः": "h", "्": "", "़": "",
}

VOWELS = set("aeiou")

# Two-character skeletons ("war" → vr, "Ali" → al) collide with far too many
# unrelated words to be evidence of topic overlap.
MIN_KEY_LENGTH = 3


@dataclass
class SeedContext:
    """What the seed video is actually about."""

    title: str
    title_query: str
    subjects: list[str] = field(default_factory=list)
    subject_keys: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    keyword_keys: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    # Primary people/orgs the story is ABOUT (e.g. Khamenei), not the region.
    primary: list[str] = field(default_factory=list)
    primary_keys: list[str] = field(default_factory=list)
    # Event/angle words (track, kill, Mossad, bunker) that define THIS story.
    angle: list[str] = field(default_factory=list)
    angle_keys: list[str] = field(default_factory=list)
    # Distinctive non-broad keys from the seed transcript for same-story checks.
    distinctive_keys: list[str] = field(default_factory=list)
    from_transcript: bool = False

    @property
    def core_keys(self) -> list[str]:
        # Prefer primary + angle so relevance isn't Iran+nuclear alone.
        ordered: list[str] = []
        for key in self.primary_keys + self.angle_keys + self.subject_keys:
            if key and key not in ordered:
                ordered.append(key)
        return ordered[:10]


def transliterate(word: str) -> str:
    if not DEVANAGARI_CHAR_RE.search(word):
        return word
    return "".join(DEV_TO_LATIN.get(ch, ch) for ch in word)


def skeleton(word: str) -> str:
    """Script-agnostic fuzzy key: कhamenei / खामेनेई → 'kmn'."""
    latin = transliterate(word).lower()
    latin = re.sub(r"[^a-z]", "", latin)
    if not latin:
        return ""
    latin = latin.replace("ph", "f").replace("z", "j").replace("q", "k")
    latin = latin.replace("w", "v").replace("x", "ks").replace("h", "")
    if not latin:
        return ""
    head, rest = latin[0], latin[1:]
    key = head + "".join(ch for ch in rest if ch not in VOWELS)
    return re.sub(r"(.)\1+", r"\1", key)


def strip_noise(text: str) -> str:
    """Remove caption markers and URLs before any term counting."""
    text = URL_RE.sub(" ", text or "")
    return CAPTION_MARKER_RE.sub(" ", text)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")]


def content_tokens(text: str) -> list[str]:
    return [t for t in tokenize(strip_noise(text)) if len(t) > 2 and t not in STOPWORDS]


def key_counts(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for token in content_tokens(text):
        key = skeleton(token)
        if len(key) >= MIN_KEY_LENGTH:
            counts[key] += 1
    return counts


def text_keys(text: str) -> set[str]:
    return set(key_counts(text))


def clean_title(title: str) -> str:
    title = re.sub(r"\s*\|\s*2D Animation\s*$", "", title or "", flags=re.I)
    title = re.sub(r"[#@]", " ", title)
    title = TITLE_NOISE_RE.sub(" ", title)
    # Trailing episode codes: "E42", "Ep 7", "S2E3"
    title = re.sub(r"\s+(?:S\d+)?E(?:p)?\s*\d+\s*$", " ", title, flags=re.IGNORECASE)
    title = re.sub(r"[|•·]+", " ", title)
    title = re.sub(r"[?!.,:;\"'\u0964\u0965]+\s*$", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def title_search_query(title: str) -> str:
    cleaned = clean_title(title)
    if ":" in cleaned:
        head = cleaned.split(":", 1)[0].strip()
        if len(head.split()) >= 2:
            return head[:120]
    return cleaned[:120]


def extract_entities(title: str, transcript: str, *, limit: int = 12) -> list[str]:
    """Proper-noun-ish phrases, trusting repeated transcript mentions over title packaging."""
    counts: Counter[str] = Counter()
    title_lower = (title or "").lower()

    for source_text, weight, min_count in ((transcript, 1, 3), (title, 8, 1)):
        local: Counter[str] = Counter()
        for run in CAPITAL_RUN_RE.findall(strip_noise(source_text)):
            phrase = re.sub(r"\s+", " ", run).strip()
            words = phrase.split()
            if not words:
                continue
            if words[0].lower() in STOPWORDS or words[0].lower() in ENTITY_BLOCKLIST:
                phrase = " ".join(words[1:])
                words = phrase.split()
                if not words:
                    continue
            if phrase.lower() in ENTITY_BLOCKLIST:
                continue
            # Skip title packaging like "Track Khamenei" when it is just the seed title.
            if phrase.lower() in title_lower and weight > 1 and len(words) <= 3:
                continue
            local[phrase] += 1
        for phrase, count in local.items():
            if count >= min_count:
                counts[phrase] += count * weight

    ranked: list[str] = []
    seen: set[str] = set()
    for phrase, _score in counts.most_common(limit * 4):
        key = phrase.lower()
        if key in seen or any(key in existing for existing in seen):
            continue
        seen.add(key)
        ranked.append(phrase)
        if len(ranked) >= limit:
            break
    return ranked


def _broad_keys() -> set[str]:
    return {skeleton(w) for w in BROAD_TOPIC_WORDS if len(skeleton(w)) >= MIN_KEY_LENGTH}


def _angle_keys() -> set[str]:
    return _hint_keys()


def is_broad_only(keys: set[str]) -> bool:
    """True when every key is a geopolitics bucket word (Iran/nuclear/war…)."""
    broad = _broad_keys()
    usable = {k for k in keys if k}
    return bool(usable) and usable <= broad


def rank_tags(
    tags: list[str],
    *,
    counts: Counter[str],
    channel: str = "",
    limit: int = 8,
) -> list[str]:
    """Keep only the uploader's tags that the transcript actually corroborates.

    Tags are hand-written subject labels, which makes them far better search
    queries than the video's own title — but they also carry channel branding
    and aspirational keywords, so each one has to be checked against what the
    transcript really discusses. Broad SEO tags like "US Iran War" / "Iran
    Nuclear Program" are rejected even when corroborated — they find every
    Iran video, not the same story.
    """
    channel_keys = {skeleton(t) for t in content_tokens(channel)}
    scored: list[tuple[float, str]] = []

    for tag in tags or []:
        words = content_tokens(tag)
        if not words:
            continue
        tag_keys = [skeleton(w) for w in words]
        tag_keys = [k for k in tag_keys if len(k) >= MIN_KEY_LENGTH]
        if not tag_keys or set(tag_keys) & channel_keys:
            continue
        if is_broad_only(set(tag_keys)):
            continue
        corroborated = [k for k in tag_keys if counts.get(k)]
        coverage = len(corroborated) / len(tag_keys)
        if coverage < 0.6:
            continue
        frequency = sum(counts.get(k, 0) for k in tag_keys)
        if frequency < 3:
            continue
        # Multi-word tags name a specific angle; single words are usually broad.
        specificity = 0.15 * min(len(tag_keys), 3)
        # Prefer tags that include a story-angle word (Mossad, assassination…).
        # Prefer tags that share a seed event-hint word when present.
        angle_bonus = 0.25 if set(tag_keys) & _hint_keys() else 0.0
        scored.append((coverage + specificity + angle_bonus + min(frequency, 200) / 400, tag.strip()))

    scored.sort(reverse=True)

    kept: list[str] = []
    kept_keys: list[set[str]] = []
    for _score, tag in scored:
        keys = {skeleton(w) for w in content_tokens(tag)} - {""}
        if any(keys <= existing or len(keys & existing) / max(1, len(keys)) > 0.75 for existing in kept_keys):
            continue
        kept.append(tag)
        kept_keys.append(keys)
        if len(kept) >= limit:
            break
    return kept


def _hint_keys() -> set[str]:
    return {skeleton(w) for w in EVENT_VERB_HINTS if len(skeleton(w)) >= MIN_KEY_LENGTH}


def token_is_event_hint(token: str) -> bool:
    """True when token is a known event verb (optional boost, not a hard gate)."""
    raw = (token or "").lower().strip()
    if raw in EVENT_VERB_HINTS:
        return True
    key = skeleton(raw)
    return len(key) >= 4 and key in _hint_keys()


def extract_primary_and_angle(
    title: str,
    transcript: str,
    *,
    entities: list[str],
    weighted: Counter[str],
    surface: dict[str, Counter[str]],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Seed-driven primary + anchors — works for any story type.

    primary  = who/what the video is about (title nouns, entities)
    angle    = what makes THIS telling specific (other title nouns, event hints,
               and high-weight non-broad transcript terms)

    No fixed Mossad/kill lexicon is required. Event-verb hints only boost
    anchors when the seed itself uses them.
    """
    primary: list[str] = []
    primary_keys: list[str] = []
    angle: list[str] = []
    angle_keys: list[str] = []
    broad = _broad_keys()

    def add_primary(term: str) -> None:
        key = skeleton(term)
        if len(key) < MIN_KEY_LENGTH or key in primary_keys or key in broad:
            return
        if token_is_event_hint(term):
            return
        primary.append(term)
        primary_keys.append(key)

    def add_angle(term: str) -> None:
        key = skeleton(term)
        if len(key) < MIN_KEY_LENGTH or key in angle_keys or key in primary_keys:
            return
        if key in broad:
            return
        blocked = {skeleton(w) for w in DISTINCTIVE_BLOCKLIST if len(skeleton(w)) >= MIN_KEY_LENGTH}
        if key in blocked and not token_is_event_hint(term):
            return
        angle.append(term)
        angle_keys.append(key)

    # Title: first non-hint nouns → primary; hints + remaining nouns → anchors.
    title_tokens = content_tokens(title)
    for token in title_tokens:
        if token_is_event_hint(token):
            add_angle(token)
        elif skeleton(token) not in broad and token.lower() not in STOPWORDS:
            if not primary:
                add_primary(token)
            else:
                # Later title nouns are usually the angle ("Track Khamenei" already
                # put Khamenei first if ordered differently — handle both).
                add_primary(token)

    # If title was "How Did They Track Khamenei", primary may be empty of person
    # because Track was hint — ensure non-hint title nouns become primary.
    for token in title_tokens:
        if not token_is_event_hint(token) and skeleton(token) not in broad:
            add_primary(token)

    for entity in entities[:6]:
        for word in content_tokens(entity):
            if token_is_event_hint(word):
                add_angle(word)
            elif skeleton(word) not in broad:
                add_primary(word)

    # Seed-specific anchors: frequent non-broad terms from the transcript.
    # Prefer terms that also appear in the title, then by frequency.
    title_key_set = {skeleton(t) for t in title_tokens if len(skeleton(t)) >= MIN_KEY_LENGTH}
    ranked: list[tuple[float, str, str]] = []
    for key, count in weighted.most_common(60):
        if key in primary_keys or key in broad or len(key) < 4:
            continue
        if key not in surface:
            continue
        word = surface[key].most_common(1)[0][0]
        if word.lower() in STOPWORDS:
            continue
        boost = 3.0 if key in title_key_set else 0.0
        if token_is_event_hint(word):
            boost += 2.0
        ranked.append((boost + min(count, 50) / 10.0, word, key))
    ranked.sort(reverse=True)
    for _score, word, _key in ranked:
        add_angle(word)
        if len(angle_keys) >= 8:
            break

    return primary[:6], primary_keys[:6], angle[:8], angle_keys[:8]


# Names/topics that show up in almost every news video — never "distinctive"
# evidence of the same story (unless they are the seed's primary).
DISTINCTIVE_BLOCKLIST = {
    "trump", "biden", "obama", "netanyahu", "america", "american", "israel",
    "iran", "nuclear", "war", "meeting", "news", "deal", "program", "modi",
    "putin", "zelensky", "china", "russia", "ukraine", "pakistan",
    "security", "intelligence", "government", "president", "minister",
    "police", "army", "military", "country", "people",
    "ट्रंप", "बाइडन", "नेतनयाहू", "अमेरिका", "ईरान", "इजराइल", "न्यूक्लियर",
    "मीटिंग", "जंग", "युद्ध", "मोदी", "पुतिन", "सिक्योरिटी", "इंटेलिजेंस",
    "सरकार", "पुलिस", "फौज", "देश", "लोग",
}


def extract_distinctive_keys(
    weighted: Counter[str],
    *,
    primary_keys: list[str],
    angle_keys: list[str],
    limit: int = 40,
) -> list[str]:
    """Seed-specific keys that are NOT broad category fillers."""
    broad = _broad_keys()
    blocked = {skeleton(w) for w in DISTINCTIVE_BLOCKLIST if len(skeleton(w)) >= MIN_KEY_LENGTH}
    keep: list[str] = []
    for key, _count in weighted.most_common(limit * 3):
        if key in broad or key in blocked:
            continue
        if len(key) < 4:
            continue
        keep.append(key)
        if len(keep) >= limit:
            break
    ordered: list[str] = []
    for key in primary_keys + angle_keys + keep:
        if key and key not in ordered:
            ordered.append(key)
    return ordered[:limit]


def build_seed_context(
    title: str,
    transcript: str = "",
    *,
    tags: list[str] | None = None,
    channel: str = "",
    max_keywords: int = 30,
    max_queries: int = 3,
) -> SeedContext:
    """Rank what the video is about, then turn that into search queries."""
    ctx = SeedContext(
        title=title or "",
        title_query=title_search_query(title),
        from_transcript=bool((transcript or "").strip()),
    )

    transcript_counts = key_counts(transcript)
    weighted = Counter(transcript_counts)
    surface: dict[str, Counter[str]] = {}
    for token in content_tokens(transcript) + content_tokens(title):
        key = skeleton(token)
        if len(key) >= MIN_KEY_LENGTH:
            surface.setdefault(key, Counter())[token] += 1

    # Title words carry intent, so weight them above ordinary transcript words.
    for token in content_tokens(title):
        key = skeleton(token)
        if len(key) >= MIN_KEY_LENGTH:
            weighted[key] += max(5, transcript_counts.get(key, 0))

    ctx.keyword_keys = [k for k, _ in weighted.most_common(max_keywords)]
    ctx.keywords = [surface[k].most_common(1)[0][0] if k in surface else k for k in ctx.keyword_keys]
    ctx.entities = extract_entities(title, transcript)
    ctx.tags = rank_tags(tags or [], counts=transcript_counts, channel=channel)

    primary, primary_keys, angle, angle_keys = extract_primary_and_angle(
        title,
        transcript,
        entities=ctx.entities,
        weighted=weighted,
        surface=surface,
    )
    ctx.primary = primary
    ctx.primary_keys = primary_keys
    ctx.angle = angle
    ctx.angle_keys = angle_keys
    ctx.distinctive_keys = extract_distinctive_keys(
        weighted,
        primary_keys=primary_keys,
        angle_keys=angle_keys,
    )

    ctx.subjects, ctx.subject_keys = build_subjects(ctx, weighted, surface)
    ctx.queries = build_queries(ctx, max_queries=max_queries)
    return ctx


def build_subjects(
    ctx: SeedContext,
    weighted: Counter[str],
    surface: dict[str, Counter[str]],
) -> tuple[list[str], list[str]]:
    """The handful of terms that define the topic, ranked, deduplicated by key."""
    subjects: list[str] = []
    subject_keys: list[str] = []
    broad = _broad_keys()

    def add(term: str, *, allow_broad: bool = False) -> None:
        key = skeleton(term)
        if len(key) < MIN_KEY_LENGTH or key in subject_keys:
            return
        if key in broad and not allow_broad:
            return
        subjects.append(term)
        subject_keys.append(key)

    # Primary person/org first, then angle — never let Iran/nuclear dominate.
    for term in ctx.primary:
        add(term)
    for term in ctx.angle:
        add(term, allow_broad=True)

    for tag in ctx.tags[:4]:
        for word in content_tokens(tag):
            add(word)
    for entity in ctx.entities[:4]:
        for word in content_tokens(entity):
            add(word)
    for key, _weight in weighted.most_common(12):
        add(surface[key].most_common(1)[0][0] if key in surface else key)

    # If we still have room, allow one broad geography anchor (Iran) last.
    if len(subjects) < 4:
        for key, _weight in weighted.most_common(8):
            if key in broad:
                add(surface[key].most_common(1)[0][0] if key in surface else key, allow_broad=True)
                break

    return subjects[:12], subject_keys[:12]


def build_queries(ctx: SeedContext, *, max_queries: int = 4) -> list[str]:
    """Primary + seed-anchor queries — never broad SEO category tags.

    Works for any story: primary is who/what; anchors are what makes this
    telling specific (derived from the seed transcript, not a fixed lexicon).
    """
    queries: list[str] = []
    title_keys = {skeleton(w) for w in content_tokens(ctx.title)} - {""}

    def too_title_like(candidate: str) -> bool:
        keys = {skeleton(w) for w in content_tokens(candidate)} - {""}
        if not keys:
            return True
        overlap = len(keys & title_keys) / max(1, len(keys))
        return overlap >= 0.8 and len(keys) <= max(3, len(title_keys))

    def add(candidate: str) -> None:
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if len(candidate) < 4 or len(queries) >= max_queries:
            return
        if any(candidate.lower() == existing.lower() for existing in queries):
            return
        keys = {skeleton(w) for w in content_tokens(candidate)} - {""}
        if is_broad_only(keys):
            return
        if too_title_like(candidate):
            return
        queries.append(candidate[:120])

    primary = [p for p in ctx.primary if p.lower() not in STOPWORDS]
    angle = [a for a in ctx.angle if a.lower() not in STOPWORDS]
    subjects = [s for s in ctx.subjects if s.lower() not in STOPWORDS and not is_broad_only({skeleton(s)})]

    # 1) Primary + seed-anchor pairs
    for p in primary[:2]:
        for a in angle[:4]:
            if skeleton(p) == skeleton(a):
                continue
            add(f"{p} {a}")
            if len(queries) >= max_queries:
                return queries

    # 2) Non-broad corroborated tags
    for tag in ctx.tags[:max_queries]:
        add(tag)

    # 3) Primary + other subjects
    for p in primary[:2]:
        for s in subjects[:4]:
            if skeleton(s) in {skeleton(p)} | _broad_keys():
                continue
            add(f"{p} {s}")
            if len(queries) >= max_queries:
                return queries

    # 4) Hindi + Latin mix for Indian channel indexes
    if len(queries) < max_queries:
        hindi = [k for k in ctx.keywords if DEVANAGARI_CHAR_RE.search(k) and k not in STOPWORDS][:3]
        latin_primary = [p for p in primary if not DEVANAGARI_CHAR_RE.search(p)][:2]
        seed_keys = set(ctx.primary_keys) | set(ctx.angle_keys)
        for hp in hindi:
            if skeleton(hp) in seed_keys:
                for lp in latin_primary:
                    add(f"{lp} {hp}")
                for a in angle[:2]:
                    if not DEVANAGARI_CHAR_RE.search(a):
                        add(f"{a} {hp}")

    if not queries and primary:
        add(primary[0])
    if not queries:
        nouns = [w for w in content_tokens(ctx.title) if w not in STOPWORDS and skeleton(w) not in _broad_keys()][:2]
        if nouns:
            add(" ".join(nouns))

    return queries


def _anchor_hits(candidate_keys: set[str], ctx: SeedContext) -> int:
    """How many seed anchors (angle + distinctive) appear in the candidate."""
    anchors = [k for k in (ctx.angle_keys + ctx.distinctive_keys[:20]) if k not in _broad_keys()]
    # Dedupe while preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for k in anchors:
        if k and k not in seen and k not in set(ctx.primary_keys):
            seen.add(k)
            ordered.append(k)
    return sum(1 for k in ordered[:20] if k in candidate_keys)


def _match_score(candidate_keys: set[str], ctx: SeedContext, *, title: str = "") -> float:
    """Title pre-filter: same primary + seed anchors, not just same category."""
    primary = ctx.primary_keys or ctx.subject_keys[:2]
    if not primary:
        return 0.0

    primary_hits = sum(1 for k in primary if k in candidate_keys)
    anchor_hits = _anchor_hits(candidate_keys, ctx)

    if not primary_hits:
        # Allow titles that name several seed anchors without the primary
        # (e.g. "Mossad bunker satellite strike") when overlap is strong.
        if anchor_hits >= 3:
            return round(0.35 + 0.05 * min(anchor_hits, 4), 3)
        return 0.0

    score = 0.35 + 0.15 * min(primary_hits, 2)
    if anchor_hits >= 2:
        score += 0.25 + 0.05 * min(anchor_hits, 4)
    elif anchor_hits == 1:
        score += 0.12
    else:
        # Primary alone ("X क्या बोले?") — below typical min_relevance 0.35.
        score = min(score, 0.30)

    return round(min(score, 1.0), 3)


def title_relevance(candidate_title: str, ctx: SeedContext) -> float:
    """Cheap pre-filter: same person/anchors, not just same country/genre."""
    return _match_score(text_keys(candidate_title), ctx, title=candidate_title)


def transcript_relevance(candidate_transcript: str, ctx: SeedContext) -> float:
    """Same-story check for any topic: primary + seed-anchor overlap.

    A related video must discuss the seed's primary subject AND share enough
    of the seed's distinctive anchors. Sharing only a broad category
    (Iran/nuclear/crime/war) is not enough.
    """
    if not candidate_transcript.strip():
        return 0.0
    candidate_keys = text_keys(candidate_transcript)
    primary = ctx.primary_keys or ctx.subject_keys[:2]
    if not primary:
        return 0.0

    primary_hits = sum(1 for k in primary if k in candidate_keys)
    if not primary_hits:
        return 0.0

    blocked = {skeleton(w) for w in DISTINCTIVE_BLOCKLIST if len(skeleton(w)) >= MIN_KEY_LENGTH}
    angle_hits = sum(
        1 for k in ctx.angle_keys
        if k in candidate_keys and k not in set(primary) | _broad_keys()
    )
    distinctive = [
        k for k in ctx.distinctive_keys[:30]
        if k not in set(primary) | _broad_keys() | blocked and len(k) >= 4
    ]
    dist_hits = sum(1 for k in distinctive if k in candidate_keys)
    anchor_hits = angle_hits + dist_hits

    # Hard gate: need seed anchors, not just the primary name in a different story.
    if angle_hits < 1 and dist_hits < 4:
        return round(0.12 + 0.04 * primary_hits + 0.03 * min(anchor_hits, 3), 3)
    if angle_hits < 2 and dist_hits < 4:
        return round(0.18 + 0.04 * primary_hits + 0.04 * min(anchor_hits, 4), 3)

    primary_fraction = primary_hits / max(1, len(primary))
    angle_fraction = angle_hits / max(1, len(ctx.angle_keys) or 1)
    dist_fraction = dist_hits / max(1, min(12, len(distinctive) or 1))

    score = (
        0.30 * min(1.0, primary_fraction)
        + 0.40 * min(1.0, angle_fraction)
        + 0.30 * min(1.0, dist_fraction)
    )
    return round(min(score, 1.0), 3)


def distinctive_details(text: str) -> set[str]:
    """Numbers and proper nouns — the details copyright treats as a selection."""
    details = {n.strip(".,") for n in NUMBER_RE.findall(text or "")}
    details |= {c.strip() for c in CAPITAL_RUN_RE.findall(text or "")}
    return {d for d in details if len(d) > 1}


def source_dominance(sources: list[tuple[str, str]]) -> dict:
    """
    Measure how concentrated the distinctive details are.

    sources: list of (label, transcript)

    When one source holds most of the unique numbers and names, "merge 3-4
    sources" cannot create a new structure on its own — the writer has to be
    told explicitly to restructure that section.
    """
    if not sources:
        return {"sources": [], "dominant_source": None, "dominant_share": 0.0, "warning": None}

    detail_sets = {label: distinctive_details(text) for label, text in sources}
    per_source_unique: dict[str, set[str]] = {}
    for label, details in detail_sets.items():
        others: set[str] = set()
        for other_label, other_details in detail_sets.items():
            if other_label != label:
                others |= other_details
        per_source_unique[label] = details - others

    total_unique = sum(len(v) for v in per_source_unique.values()) or 1
    breakdown = [
        {
            "source": label,
            "unique_details": len(unique),
            "share": round(len(unique) / total_unique, 3),
        }
        for label, unique in per_source_unique.items()
    ]
    breakdown.sort(key=lambda item: item["share"], reverse=True)

    top = breakdown[0]
    warning = None
    if top["share"] >= 0.5 and len(sources) > 1:
        warning = (
            f"{top['source']} holds {top['share'] * 100:.0f}% of all unique numbers and names. "
            "Merging cannot resequence what only one source contains — the beats built on that "
            "source must be deliberately restructured and its detail selection thinned."
        )

    return {
        "sources": breakdown,
        "dominant_source": top["source"],
        "dominant_share": top["share"],
        "warning": warning,
    }
