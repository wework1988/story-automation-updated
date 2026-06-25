# Storyboard Pipeline — Bifurcated for ChatGPT (Crime-Section)

The original `template/master-prompt` is a single ~1850-line file covering all
3 production stages. It is too expensive (and too long) to run as one ChatGPT
call. This folder splits it into 3 standalone, self-contained files — one per
stage — so each can be pasted into a fresh ChatGPT chat and run independently.

> **Crime-section context:** these stages turn a finished narrative script
> (typically the output of `crime-section/template/story-writing-master-prompt`)
> into a per-scene image + motion prompt set for 2D-animation rendering of
> Hindi true-crime / mystery / unsolved-case stories. The pipeline is
> genre-agnostic but tuned to crime-section visual conventions: muted palette,
> documentary realism, restrained gore, victim respect, hostile-actor menace
> coding, and clean evidence-room / interrogation-room / discovery-scene
> staging. See "Crime-section visual conventions" below for sub-genre hints.

Each file embeds:

- the relevant SHARED LIBRARY rules,
- the stage's own spec,
- the input slots that stage needs,
- a final TASK instruction.

You do NOT need the master file to use these. Each stage file is fully
self-contained.

## Files

Source templates in this folder keep the names `stage-a-story-config.md`, etc. When you run `helper/create-story-skelton`, outputs land in `stories/<name>/`:

**Root:** `FULL_STORY.txt`, `output_config_<name>.md`, `output_story_breakdown_<name>.md`, `prompt.txt`

**`template/`:** verbatim copies of `stage-a-story-config.md`, `stage-b-scene-breakdown.md`, `stage-c-image-motion.md` (renamed only — same content as the bifurcated-template sources)

**Cross-stage assets:** `character.txt` is the locked character library — verbatim, authoritative visual descriptions for recurring characters (e.g. AMIT SHAH, MODI, AJIT DOVAL). It is consumed by every stage that has a `CHARACTER_LIBRARY:` input slot. See "Locked Character Library" below.

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
is library-locked carries a `Library lock:` tag with the matched KEY.

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
<KEY> — Character (<context label>)
================================================================================

<verbatim visual description body...>
```

The `<KEY>` (e.g. `AMIT SHAH`, `MODI`, `AJIT DOVAL`) is the matching
identifier. The body should be written in archetype phrasing
(e.g. "a senior Indian home minister figure") so it is compliant with
the no-real-name rule for output (SHARED §4) — names appear only inside
section headers, which are pipeline plumbing, never copied to image
prompts.

### How matching works

Each stage's spec implements `SHARED §12 — LOCKED CHARACTER LIBRARY`:

1. Stage A scans `FULL_STORY` for recurring characters and matches them
   against the `<KEY>` headers in `CHARACTER_LIBRARY` (after
   normalisation: uppercase, trim, drop honorifics, whole-word
   substring match). Characters that match are flagged `LIBRARY-LOCKED`
   in the roster and listed in `CHARACTER LIBRARY MATCHES`.
2. Stage B reads the lock from the `STORY CONFIG BLOCK` and tags every
   scene's metadata with `Library lock: <KEY>` whenever a locked
   character is the main / supporting subject of that scene.
3. Stage C resolves each `Library lock:` tag against the
   `CHARACTER_LIBRARY` slot and copies the **LOCKED CHARACTER ANCHOR**
   (the character-only descriptive sentences — typically the
   `Main subject:` / `Character appearance:` / `Clothing:` portions of
   the locked body) verbatim into the IMAGE PROMPT's Foreground or
   Midground. Scene-specific staging (current action, gaze, hand
   placement, props) is added around the anchor, never inside it.

### Updating the library

The library is expected to grow. To add a new character:

1. Append a new block to `character.txt` using the same equals-separator
   header format. Use a unique `<KEY>` (typically the canonical name in
   ALL CAPS).
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

## Crime-section visual conventions

The shared rules in each stage already cover hostile-actor menace coding
(`SHARED §2`), region/origin mapping (`SHARED §3`), public-figure protection
(`SHARED §4`), character consistency (`SHARED §5`), and universal negatives
(`SHARED §11`). These work as-is for every crime-section sub-genre. Below
are the sub-genres and their typical visual anchors so you can sanity-check
the Stage A output before running Stage B / C.

| Sub-genre                   | Typical environments                                  | Primary visual anchor                                        | Atmosphere family                          |
|-----------------------------|-------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------|
| Domestic / relationship murder | bedroom, bathroom, drawing room, kitchen, courtyard | victim's body, knife/hammer, blood-stained sheet, sealed drum | quiet betrayal, suburban dread             |
| Honeymoon / disappearance   | hotel room, mountain trail, waterfall ravine, cab     | discarded scooty, missing call screen, body in khaai         | tourist-paradise turned trap               |
| Workplace / nexus / racket  | open-plan BPO floor, pantry, HR room, parking lot     | CCTV bank, employee-of-month plaque, deleted chat printout   | corporate veneer hiding rot                |
| Underworld / mafia / gang   | safe-house, encounter spot, court compound, jail van  | weapon stash, a famous face on TV, an officer's holster      | territory + power + impending fall         |
| Cyber-fraud / radicalisation| cyber-cell room, cheap rented PG, prayer corner, café| laptop trail, CDR printout, hidden phone, foreign-handler map| isolation + grooming + hidden funding      |
| Mystery / unsolved (Mode B) | port edge, abandoned road, decades-old archive       | a single object that returns again and again (boat, drum, file) | unanswered question, atmospheric stillness |
| Historical / international heist | bank vault, presidential palace, motorcade tunnel | ledger, currency stack, a single signed slip                 | regime power + impossible scale            |

Crime-section visual rules to keep in mind:

- **Victim respect.** Victim faces are clearly human, not stylised into
  caricature. No glamour, no gore-zoom. Discovery scenes lean on neighbours'
  faces, officer reaction shots, and one anchor object (drum, sheet, ravine).
- **Perpetrator menace without communal coding.** `SHARED §2` requires
  hostile-actor menace coding when the story explicitly identifies a
  perpetrator. A muskan / sonam / priyanka type "domestic mastermind" reads
  as a calm, calculating figure with cold eyes — not as a generic
  "innocent housewife". Beard-discipline / skullcap / pakol coding is
  reserved for stories where the source explicitly identifies a hostile
  network actor — never inherited from religion or region alone.
- **Investigation visuals.** Lean on CCTV monitor walls, evidence tables
  with bagged items, CDR printouts, deleted-chat-recovery laptops,
  drone-camera frames over ravines, and quiet interrogation rooms with one
  tube light and a single phone on the table.
- **Aftermath.** Family doorways, an empty bedroom, a child's photo on a
  wall, a court-bench wide shot — these read stronger than press-conference
  podiums, which are aftermath documentation, not story.
- **Sensitive content.** No readable religious text, party symbols,
  extremist slogans, FIR numbers, BNS section headings on screen, or
  recognisable financial-account screens. Communicate gravity through
  staging, not through readable detail.

Pair these conventions with the upstream narrative prompt
(`crime-section/template/story-writing-master-prompt`) and the locked
character library (`character.txt`) so Stage A's roster, Stage B's scene
metadata, and Stage C's image prompts stay consistent across the whole
~80–110 scene set.

## Source

Bifurcated from `../template/master-prompt` (STORYBOARD MASTER PROMPT —
UNIFIED v2.1). Rule semantics are preserved one-for-one; only the dispatcher,
input slots, and per-file framing differ.
