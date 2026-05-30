# Storyboard Pipeline — Bifurcated for ChatGPT

**Package:** This directory is **`general-story/bifuracted-template/`**. Customise these stage files for general (non-crime-section) workflows; `general-story/run_with_params.sh` loads them automatically (via `--crime-root`). Paths below that mention `helper/create-story-skelton` apply to **`general-story/helper/`** when working in this package.

---

The original `template/master-prompt` is a single ~1850-line file covering all
3 production stages. It is too expensive (and too long) to run as one ChatGPT
call. This folder splits it into 3 standalone, self-contained files — one per
stage — so each can be pasted into a fresh ChatGPT chat and run independently.

Each file embeds:

- the relevant SHARED LIBRARY rules,
- the stage's own spec,
- the input slots that stage needs,
- a final TASK instruction.

You do NOT need the master file to use these. Each stage file is fully
self-contained.

## Files

**Automation note:** `crime-section/helper/deepseek_pipeline.py` splits Stage A/B/C templates at the exact line **`PART 3 — INPUT SLOTS`** (see constant `PART3_MARKER`). Custom Stage B documents must keep that heading text (with optional `(fill these before sending)`), and must use the **same brace placeholders** as crime-section for `STORY_CONFIG_BLOCK`, `FULL_STORY`, and `CHARACTER_LIBRARY` — see `crime-section/helper/deepseek_pipeline.py` (`PH_*` constants).

---

Source templates in this folder keep the names `stage-a-story-config.md`, etc. When you run `helper/create-story-skelton`, outputs land in `stories/<name>/`:

**Root:** `FULL_STORY.txt`, `output_config_<name>.md`, `output_story_breakdown_<name>.md`, `prompt.txt`

**`template/`:** verbatim copies of `stage-a-story-config.md`, `stage-b-scene-breakdown.md`, `stage-c-image-motion.md` (renamed only — same content as the bifurcated-template sources)

**Cross-stage assets:** `character.txt` is the locked character library — authoritative visual descriptions for recurring characters keyed by neutral IDs (e.g. `CHAR_HOME_01`, `CHAR_PM_01`, `CHAR_NSA_01`). It is consumed by every stage that has a `CHARACTER_LIBRARY:` input slot. See "Locked Character Library" below.

| File | Stage | Reads | Produces |
|------|-------|-------|----------|
| `stage-a-story-config.md` | A — Story Config Engine | `FULL_STORY`, `CHARACTER_LIBRARY` | `STORY CONFIG BLOCK` |
| `stage-b-scene-breakdown.md` | B — Scene Breakdown Engine | `STORY CONFIG BLOCK`, `FULL_STORY`, `CHARACTER_LIBRARY` | `LOCKED SCENE BREAKDOWN` |
| `stage-c-image-motion.md` | C — Image + Motion Engine | `STORY CONFIG BLOCK`, `LOCKED SCENE BREAKDOWN`, `CHARACTER_LIBRARY`, `SCENE_RANGE` | `IMAGE PROMPT` + `DIGEN MOTION PROMPT` per scene in `SCENE_RANGE` |

## Pipeline flow

```
Story (Hindi / Hinglish / English)  →  keep in FULL_STORY.txt (repo) or paste at slot below
   │
   ▼
STAGE A — open `stories/<name>/template/STORY_Config_{story_name}.md` (same content as `stage-a-story-config.md`)  +  FULL_STORY
   │   produces  →  STORY CONFIG BLOCK
   ▼
STAGE B — open `template/Story_scene_breakdown_{story_name}.md` (same as `stage-b-scene-breakdown.md`)  +  STORY CONFIG BLOCK + FULL_STORY
   │   produces  →  LOCKED SCENE BREAKDOWN  (≈80–110 scenes)
   ▼
STAGE C — open `template/<story_name>_stage-c-image-motion.md` (same as `stage-c-image-motion.md`)  +  STORY CONFIG BLOCK + LOCKED SCENE BREAKDOWN + SCENE_RANGE
        produces  →  IMAGE PROMPT + DIGEN MOTION PROMPT for each scene in SCENE_RANGE
        repeat in fresh chats with new SCENE_RANGE values
        until all scenes from the breakdown are covered
```

## How to use each stage with ChatGPT

For every stage:

1. Open a NEW ChatGPT chat (don't reuse a chat across stages — context bloat
   makes the model lazy).
2. Open the stage file, copy its FULL contents.
3. Paste as your first message.
4. Scroll to the bottom of that pasted message and fill in the input slots
   between the curly braces (`{ ... }`). Keep the rest of the file untouched.
5. Send. The model will return only that stage's output, in the strict format
   defined inside the file.
6. Save the output. It is the input to the next stage.

### Stage A — Story Config

Slot to fill:

- `FULL_STORY:` paste the full Hindi / Hinglish / English story.
- `OPTIONAL_GENRE_OR_TONE:` (optional) genre or tone hint.
- `CHARACTER_LIBRARY:` paste the full contents of `character.txt` (or
  leave blank / `NONE` if you don't want any character locked).

Output: a single `STORY CONFIG BLOCK`. Save it verbatim. Any character
matched against the library is tagged `LIBRARY-LOCKED` in the
`RECURRING CHARACTER ROSTER` and listed in the new `CHARACTER LIBRARY
MATCHES` section.

### Stage B — Scene Breakdown

Slots to fill:

- `STORY_CONFIG_BLOCK:` paste the Stage A output verbatim.
- `FULL_STORY:` paste the same story used in Stage A.
- `CHARACTER_LIBRARY:` paste the same `character.txt` content used in
  Stage A.

Output: a `LOCKED SCENE BREAKDOWN` with ~80–110 scenes (depends on story
length). Save it verbatim. Each scene whose main / supporting subject
is library-locked carries a `Library lock:` tag with the matched neutral ID.

### Stage C — Image + Motion (run multiple times)

Stage C is the heavy stage. Each `IMAGE PROMPT` is normally >3000 characters,
so ChatGPT cannot generate all 80–110 scenes in one call. You batch them.

Slots to fill (once per batch):

- `STORY_CONFIG_BLOCK:` paste Stage A output.
- `LOCKED_SCENE_BREAKDOWN:` paste Stage B output.
- `CHARACTER_LIBRARY:` paste the same `character.txt` content used in
  Stage A and Stage B.
- `SCENE_RANGE:` e.g. `Scenes 1–10`.

Run the file in a fresh chat for each batch. Suggested batch sizes:

- Safe: 5–8 scenes per call.
- Aggressive: 10 scenes per call (may hit length limits).

If the model stops early, it appends a single trailing line:
`NEXT_RANGE: Scenes X–Y`
Use that as the `SCENE_RANGE` in your next chat.

Continue batching until all scenes from the LOCKED SCENE BREAKDOWN are done.

## Locked Character Library (`character.txt`)

The `character.txt` file is a growing, authoritative library of visual
descriptions for recurring characters. Each block in the file looks
like:

```
================================================================================
<CHARACTER_ID> — Character (<context label>)
================================================================================

MATCH ALIASES — PIPELINE ONLY, NEVER COPY TO IMAGE PROMPT:
<source names, role phrases, aliases, or continuity labels used only for matching>

LOCKED CHARACTER ANCHOR — COPY VERBATIM EVERY TIME:
<character-only visual description body...>

NEGATIVE IDENTITY FIREWALL:
<optional traits to exclude so other character identities do not bleed in>
```

The `<CHARACTER_ID>` (e.g. `CHAR_HOME_01`, `CHAR_PM_01`, `CHAR_NSA_01`) is the matching
identifier. Prefer neutral IDs rather than public names. Use `MATCH ALIASES`
for source names, titles, and role phrases that help Stage A/B match the story
to the right ID. The anchor should be written in archetype phrasing
(e.g. "a senior Indian home minister figure") so it is compliant with
the no-real-name rule for output (SHARED §4). Aliases and IDs are pipeline
plumbing and must never be copied to image prompts.

### How matching works

Each stage's spec implements `SHARED §12 — LOCKED CHARACTER LIBRARY`:

1. Stage A scans `FULL_STORY` for recurring characters and matches them
   against each block's `MATCH ALIASES` and neutral `<CHARACTER_ID>` in
   `CHARACTER_LIBRARY` (after normalisation: uppercase, trim, drop honorifics,
   whole-word substring match). Characters that match are flagged
   `LIBRARY-LOCKED` in the roster and listed in `CHARACTER LIBRARY MATCHES`.
2. Stage B reads the lock from the `STORY CONFIG BLOCK` and tags every
   scene's metadata with `Library lock: <CHARACTER_ID>` whenever a locked
   character is the main / supporting subject of that scene.
3. Stage C resolves each `Library lock:` tag against the
   `CHARACTER_LIBRARY` slot and copies the **LOCKED CHARACTER ANCHOR**
   verbatim into the IMAGE PROMPT's Foreground or Midground. Scene-specific
   staging (current action, gaze, hand placement, props) is added around the
   anchor, never inside it. The neutral ID itself is not printed in IMAGE
   PROMPT, NEGATIVE, or DIGEN MOTION PROMPT.

### Updating the library

The library is expected to grow. To add a new character:

1. Append a new block to `character.txt` using the same equals-separator
   header format. Use a unique neutral `<CHARACTER_ID>` such as
   `CHAR_HOME_01`, then add matching names/roles under `MATCH ALIASES`.
2. Re-run all three stages with the updated `character.txt` content
   pasted into each `CHARACTER_LIBRARY:` slot.
3. The next run picks up the new entry; old entries removed from
   `character.txt` cease to lock on the next run.

### When the library doesn't match a character

If a character in the story has no library entry, all three stages fall
back to inference per `SHARED §3` (region/origin/ideology mapping) and
`SHARED §5` (character consistency). No lock is applied.

### What about the same story with different libraries?

Each fresh run is independent. The `CHARACTER_LIBRARY` slot is
authoritative for that specific run only — there is no caching between
chats.

## Tips

- Always start each stage in a fresh chat — old context degrades quality.
- Do not edit the rules inside the stage file. Only fill the input slots at
  the bottom.
- If Stage A or Stage B output is missing a section the next stage needs,
  re-run that earlier stage rather than guessing.
- The `||` terminator at the end of each `IMAGE PROMPT` is mandatory — it is
  used by downstream image-generation tooling. Don't strip it.
- Public figure names must NOT appear in any output outside the verbatim
  `Hindi line:` field. The rules enforce this; do not override.

## Source

Bifurcated from `../template/master-prompt` (STORYBOARD MASTER PROMPT —
UNIFIED v2.1). Rule semantics are preserved one-for-one; only the dispatcher,
input slots, and per-file framing differ.
