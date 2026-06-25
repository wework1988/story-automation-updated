================================================================================
STORYBOARD PIPELINE — STAGE B: SCENE BREAKDOWN ENGINE (standalone)
Derived from STORYBOARD MASTER PROMPT — UNIFIED v2.6 — SAFE 5-SECOND AUDIO FIT
================================================================================

HOW TO USE THIS FILE WITH CHATGPT
1. First, run Stage A (stage-a-story-config.md) and save its STORY CONFIG BLOCK output.
2. Open a new ChatGPT chat for Stage B.
3. Copy this ENTIRE file and paste it as your first message.
4. At the very bottom, fill in the input slots:
      STORY_CONFIG_BLOCK: <-- paste Stage A output
      FULL_STORY:        <-- paste the same Hindi/Hinglish/English story
      CHARACTER_LIBRARY: <-- paste locked character library from Stage A, or NONE
5. Send. ChatGPT will return ONLY the LOCKED SCENE BREAKDOWN.
6. Save that LOCKED SCENE BREAKDOWN — it is the input to Stage C.

PIPELINE POSITION
   Story (Hindi / Hinglish / English)
        |
        v
   STAGE A — STORY CONFIG ENGINE
        produces: STORY CONFIG BLOCK
        |
        v
   >>> STAGE B — SCENE BREAKDOWN ENGINE (this file) <<<
        produces: LOCKED SCENE BREAKDOWN
        |
        v
   STAGE C — IMAGE + MOTION PROMPT ENGINE
        produces: IMAGE PROMPT + DIGEN MOTION PROMPT per locked scene


================================================================================
PART 0 — DISPATCHER (locked to STAGE B)
================================================================================

ACTIVE STAGE: B

Behavior:
- Execute ONLY the STAGE B SPEC below.
- Read the STORY_CONFIG_BLOCK + FULL_STORY.
- Read the CHARACTER_LIBRARY input slot if non-empty, and apply
  SHARED §12 (locked character library) to attach a "Library lock:"
  tag to every scene whose main / supporting subject matches a
  LIBRARY-LOCKED character recorded in the STORY CONFIG BLOCK.
- Segment into 5-second visual beats with context-rich metadata (SHARED §13)
  so Stage C can ground each image in story arc, moment, continuity,
  environment, and concrete props.
- Enforce the SAFE 5-SECOND AUDIO FIT TARGET: every Hindi line should feel
  recordable within one natural 5-second narration beat. Target 8–14 spoken
  words. Allow 15–18 spoken words only when the line is smooth, visually
  indivisible, and still sounds natural in 5 seconds. Treat 19+ spoken words as
  a must-split review, and treat 22+ spoken words as almost always invalid
  unless the source sentence is truly indivisible. Keep 95 visible characters
  as a readability warning, not the main pacing test. Split only at safe
  complete-unit boundaries without breaking a sentence mid-thought, without
  comma-stubs, and without violating the ONE-VISUAL-BEAT MANDATE.
- Output ONLY the LOCKED SCENE BREAKDOWN in the exact format defined in this file.
- Do NOT generate IMAGE PROMPT or DIGEN MOTION PROMPT.
- Do NOT add commentary, analysis, or explanation outside the breakdown.
- If the pipeline sends CONTEXT OVERLAP + AUTHORITATIVE CONTINUATION rails in FULL_STORY, treat overlap as already-filmed recap only; NEVER emit Scene entries exclusively for overlap text; continue strict chronological narration only from the authoritative body; quotations in “Hindi line:” must stay verbatim script.
- NEVER insert extra LOCKED SCENE BREAKDOWN headings, excerpt titles, or “END OF …” ribbons between Scene blocks—the pipeline merges slices into one locked file without those separators.


================================================================================
PART 1 — SHARED LIBRARY (read by this stage)
================================================================================

This library is the single source of truth for cross-stage rules. The Stage B
spec references it by section number. Do NOT inline-rewrite these rules inside
the stage spec.

--------------------------------------------------------------------------------
SHARED §1 — GLOBAL STYLE LOCK
--------------------------------------------------------------------------------

Use this visual language implicitly when describing visual defaults:

2D digital animated illustration; cinematic hand-drawn 2D matte painting; clean
hand-drawn line art; flat cel shading; minimal texture; simplified forms with
strong readability; documentary realism; restrained stylisation; region-accurate
facial features; historically grounded environments; muted documentary color
palette unless the scene clearly requires warmer or brighter tonal treatment;
no photorealism; no 3D rendering; no ray tracing; no global illumination;
no depth of field blur; no cinematic lens artifacts; no glossy CGI finish;
no hyper-detailed skin texture; no HDR realism.

Always implicitly avoid: photorealistic; ultra realistic; 3D render; CGI;
ray tracing; global illumination; lens flare; bokeh; depth of field blur;
bloom; volumetric fantasy light; hyper-detailed pores; photo textures;
futuristic design unless era supports it; neon colors unless era and setting
clearly support them; watermark; logo; text overlay; poster layout;
empty stage-like backgrounds.

--------------------------------------------------------------------------------
SHARED §2 — HOSTILE ACTOR VISUAL MENACE (MANDATORY)
--------------------------------------------------------------------------------

A "hostile actor" means: terrorist, extremist, radical handler, hostile
recruiter, radical propagandist, violent conspirator, terror commander,
operative, handler, suspect linked to hostile activity, criminal operative,
or hostile-network member — as identified by the source story or the
STORY CONFIG BLOCK.

§2.1 ABSOLUTE MANDATE
When a hostile actor appears in main subject or supporting subject, the
image MUST visually communicate menace clearly enough that any viewer reads
the figure as a hardened militant / extremist / threatening operative within
1–2 seconds of glancing at the frame. A hostile actor that looks like an
ordinary passer-by, a regular working-class man, a neutral civilian, a
gentle uncle, a humble teacher, or a calm stranger is a FAILED prompt.

§2.3 NEVER DESCRIBE HOSTILE ACTORS AS
gentle • calm in a peaceful way • soft-faced • innocent • kind-looking •
warm • graceful • saintly • pure • humble • harmless • charming • heroic •
stylish • attractive in a beauty sense • charismatic • emotionally
sympathetic • noble • ordinary • regular • neutral civilian • clean-shaven
modern man (unless story explicitly says disguise) • a normal passer-by •
a working-class everyman • an unremarkable face in the crowd •
documentary-flat • blank • generic.

§2.5 CONTINUITY
Hostile actors must remain visually tense, secretive, hardened, and morally
threatening across all scenes UNLESS the story explicitly shows disguise or
deception.

§2.6 CIVILIAN SEPARATION RULE (UNCHANGED — STILL MANDATORY)
Ordinary civilians from the same religion / region / ethnicity / clothing
family as hostile actors must REMAIN ordinary civilians — never inherit
hostile coding because of beard, skullcap, prayer cap, shalwar kameez,
hijab, mosque background, or religious clothing alone. Apply hostile coding
ONLY when the story or STORY CONFIG BLOCK clearly identifies the person as
a hostile actor.

(Stage B uses §2 mainly for: scene-context-label strengthening, recurring
hostile-character labelling, and split decisions where mood beats vs hostile
operational beats must NOT be merged.)

--------------------------------------------------------------------------------
SHARED §3 — REGION / ORIGIN / IDEOLOGY VISUAL MAPPING
--------------------------------------------------------------------------------

§3.3 ROLE CATEGORY
ordinary civilian • family member • journalist • police officer • military
officer • intelligence official • politician/public figure • cyber analyst •
hostile actor • terrorist commander • extremist recruiter • radical
propagandist • criminal operative • handler • suspect • victim • student •
crowd.

§3.5 APPEARANCE COMBINATION RULE
Visual styling = origin + region + era + class + role + ideology + story
context. Do NOT apply hostile coding only because of religion, ethnicity,
country, beard, clothing, or region. Apply militant/extremist coding ONLY
when the story identifies the person/group as terrorist, extremist, militant,
radical handler, hostile recruiter, propagandist, violent conspirator, terror
commander, operative, handler, or suspect linked to hostile activity.

(Stage B uses §3 mainly for: identifying which characters need labelled
roster tracking and for choosing main-subject labels per scene metadata.)

--------------------------------------------------------------------------------
SHARED §4 — PUBLIC FIGURE & NO-EXPLICIT-NAME RULE
--------------------------------------------------------------------------------

§4.1 SCOPE
Applies to politicians, ministers, advisors, military leaders, intelligence
chiefs, prime-ministerial figures, and any other recognizable real public
person.

§4.2 ABSOLUTE NAME RULE
Real names of public figures may appear ONLY where the original source itself
already contains the name inside "Hindi line:". They MUST NOT appear anywhere
else in any generated output, in any stage. This includes: scene context
labels, IMAGE PROMPT prefix, IMAGE PROMPT body, NEGATIVE section, DIGEN MOTION
PROMPT, metadata fields, breakdown notes, or any character reference outside
"Hindi line:".

§4.3 ARCHETYPE CONVERSION
Outside "Hindi line:", convert public figures into descriptive archetypes:
physical appearance, role, age, dress, posture, presence.

§4.4 STRICTLY FORBIDDEN OUTSIDE "Hindi line:"
- Narendra Modi, Amit Shah, Ajit Doval, or any public figure's exact name
- initials or shortened forms clearly identifying the same person
- explicit identity labels, readable nameplates, readable insignia, readable
  party symbols
- exact-likeness instructions; rely on physical archetype description instead

§4.5 CONTINUITY
If a public figure appears repeatedly, lock the same descriptive archetype
across all relevant scenes.

--------------------------------------------------------------------------------
SHARED §5 — CHARACTER CONSISTENCY ENGINE
--------------------------------------------------------------------------------

§5.1 STABLE ATTRIBUTES (must remain constant across scenes unless story
forces a change)
age range; body build; face shape; skin tone; hairstyle; facial hair;
glasses; clothing family appropriate to story point; profession/status cues;
emotional baseline; posture language.

§5.2 CLOTHING-CHANGE TRIGGERS (only these justify a change)
time passage; location change; official setting change; disguise change;
day/night transition; uniform change.

§5.3 INFERENCE
If a recurring character first appears without enough textual detail, infer a
stable design from: era + geography + profession + class + role + context.
Lock the inferred identity and reuse it consistently.

§5.4 HOSTILE RECURRING CHARACTERS
Maintain the same threatening visual identity across scenes.

(Stage B uses §5 to keep recurring characters trackable through scene labels
and metadata, NOT to write visual descriptions.)

--------------------------------------------------------------------------------
SHARED §6 — SOURCE TEXT (HINDI LINE) PRESERVATION
--------------------------------------------------------------------------------

The "Hindi line:" field carries the original Hindi/Hinglish/English wording.
Across all stages:

- Preserve exactly. Copy verbatim from source.
- Do NOT rewrite, paraphrase, summarize, simplify, correct grammar, add
  missing words, remove words, translate, modernize, or change punctuation
  unnecessarily.
- The only allowed modification is segmentation between scenes (Stage B only).

If the original Hindi line itself contains a public figure's real name, that
name is preserved ONLY inside "Hindi line:" (never repeated elsewhere — see
SHARED §4).

--------------------------------------------------------------------------------
SHARED §7 — ABSTRACT / CONCEPTUAL LINE TRANSLATION
--------------------------------------------------------------------------------

§7.1 IDENTIFICATION
Conceptual lines have no concrete subject or action — for example:
"तनाव नया नहीं था", "सन्नाटा अलग था", "Narrative की दिशा dangerous थी",
"यह सिर्फ video फैलाने की बात नहीं थी".

§7.2 IN STAGE B (BREAKDOWN)
Do not split abstract lines automatically. Merge short connected abstract
lines when:
- the same image can represent both;
- combined length is not too long;
- there is no location/subject/object/action/camera-scale change.
Do NOT merge abstract atmosphere with concrete operational detail (officers,
screens, files, maps, devices) — split those.

--------------------------------------------------------------------------------
SHARED §8 — SCENE CONTEXT LABEL RULES
--------------------------------------------------------------------------------

§8.1 SHAPE
3 to 8 words; title-like; concise; file-name friendly; no quotes; no slashes;
no punctuation overload; describes role, setting, action, mood, threat, or
object — not real names.

§8.2 NAME RULE
- Never use a public figure's real name.
- Avoid all real personal names where possible; describe role/archetype
  instead.

§8.3 HOSTILE-SCENE STRENGTHENING
If a scene includes a hostile actor, do NOT use soft labels. Strengthen the
label with grounded threat language. Examples:

  Soft (forbidden)              →   Stronger (preferred)
  Young Man Watches Video       →   Hostile Recruiter Watches Screen
  Religious Speaker Talks       →   Radical Handler Controls Room
  Group Listening Quietly       →   Suspicious Group Receives Message
  Man Uses Phone                →   Threat Network Studies Phone
  Calm Speaker Addresses Room   →   Hostile Propagandist Shapes Narrative
  Gentle Man In Room            →   Criminal Handler Waits In Shadow

§8.4 GOOD EXAMPLES
Opening Cyber Room Silence • Screens Replay Suspicious Video • Officer
Detects Forwarding Pattern • Digital Weapon Metaphor • Network Map Under
Review • Closed Room Security Briefing • Device Seizure Evidence Table •
Silent Street Under Watch • Domestic Phone Anxiety • Final Confirmation
Moment • Administrative Power Before Decision • Silent Strategist Studies
Thread Map • Hidden Propaganda Clip Reviewed.

§8.5 BAD EXAMPLES
This Scene Shows A Very Important Thing • Modi Takes Decision • Ajit Doval
Looks At Map • Amit Shah Sitting In Room • PM Scene • Very Dramatic Scene •
Innocent Looking Terrorist • Peaceful Extremist Speaker.

--------------------------------------------------------------------------------
SHARED §9 — CAMERA SCALE VOCABULARY
--------------------------------------------------------------------------------

Choose ONE per scene. Do not flatten every scene to the same scale.

- Wide establishing — geography, atmosphere, public space, institutional
  exterior, room-level mood.
- Medium-wide environmental — streets, rooms, checkpoints, offices, domestic
  interiors, investigation spaces, suspicious rooms, hostile gathering spaces.
- Medium character beat — posture, tension, interaction, restrained facial
  expression, guarded eye contact, body language.
- Tight object detail — phone, file, laptop, map, evidence item, hand
  gesture, door lock, document, screen, bag, device, key object.
- Over-shoulder analysis — digital evidence, investigation screens, planning
  tables, maps, laptops, propaganda videos, strategic review.
- Doorway interior view — domestic interiors, hidden observation, quiet
  tension, family clusters, secretive gatherings, room-entry perspectives.
- Elevated room view — monitoring rooms, meetings, evidence rooms, command
  rooms, institutional spaces, suspicious group rooms.
- Elevated street view — lanes, checkpoints, public tension, movement,
  crowds, deployment, exterior watch, suspicious street movement.
- Close reaction frame — emotional shock, realization, silence, fear,
  dialogue impact, hostile suspicion, predatory focus.
- Evidence-table view — seized devices, files, phones, maps, documents,
  coded notes without readable text, forensic review.

--------------------------------------------------------------------------------
SHARED §10 — VISUAL BEAT TYPE VOCABULARY
--------------------------------------------------------------------------------

Choose ONE per scene from:
Establishing atmosphere • Operational detail • Character reaction • Dialogue
turning point • Investigation analysis • Digital evidence • Domestic
reaction • Street tension • Closed-room decision • Field movement • Raid
preparation • Device seizure • Forensic review • Network mapping •
Consequence beat • Emotional punch • Climax beat • Aftermath beat •
Abstract commentary visualized physically.

Note: In the full crime-section pipeline, SHARED §11 is UNIVERSAL NEGATIVES
(sensitive content), defined in Stage A / Stage C — Stage B does not restate
it. Per-scene context fields for Stage B are SHARED §13.

--------------------------------------------------------------------------------
SHARED §12 — LOCKED CHARACTER LIBRARY
--------------------------------------------------------------------------------

§12.1 PURPOSE
Some recurring characters have an authoritative, locked visual description
maintained outside the story file in a character library. Stage B's role
is to PROPAGATE the lock — never to render the locked body, but to make
sure every per-scene main / supporting subject correctly carries the
matched library KEY so Stage C can copy the locked body verbatim into
the IMAGE PROMPT.

§12.2 INPUT SOURCE
Stage B receives the library through the CHARACTER_LIBRARY input slot
in PART 3 of this stage file. The user pastes the same library text
they pasted into Stage A. Stage B also receives the STORY_CONFIG_BLOCK,
which already records all matched characters in its CHARACTER LIBRARY
MATCHES section and tags them LIBRARY-LOCKED in the RECURRING CHARACTER
ROSTER. The STORY_CONFIG_BLOCK is the primary truth for which characters
are locked; the CHARACTER_LIBRARY slot is provided so Stage B can
disambiguate role references in the FULL_STORY (e.g. "the home
minister") to the right KEY when needed.

§12.3 LIBRARY FORMAT
Same parsing rules as Stage A's SHARED §12.3. Each block begins with
an equals separator, a header "<KEY> — Character (<context label>)",
another equals separator, then the verbatim body until the next block
or end-of-input.

§12.4 STAGE B RESPONSIBILITIES
For each scene:
1. Identify the main subject and any supporting subjects.
2. For each subject, determine whether it corresponds to a
   LIBRARY-LOCKED character (per the STORY CONFIG BLOCK roster).
   Match by archetype label OR by Hindi-line role mention OR by the
   STORY CONFIG BLOCK's recorded library reference key.
3. If yes, attach a "Library lock:" tag to the scene with the matching
   KEY (or comma-separated KEYs when multiple locked subjects appear).
4. If no subject is locked, emit "Library lock: NONE" or omit the field
   entirely (per SCENE METADATA REQUIREMENTS in PART 2).
5. Do NOT copy the library body into the breakdown. Do NOT paraphrase
   it. The body is resolved by Stage C.

§12.5 NAME RULE INTERACTION (SHARED §4)
The library KEY may be a real public-figure name. SHARED §4 still
applies. The KEY is permitted ONLY in the "Library lock:" tag of a
scene's metadata block — pipeline plumbing, not narrative output. It
MUST NOT appear in Hindi lines (unless already there in the source),
in scene context labels, in main subject descriptions, in main
location descriptions, in Current story arc, Current story context,
Visual continuity anchor, Surrounding environment, Supporting visual
elements, or breakdown notes — or anywhere else in the breakdown.

§12.6 ABSENCE OF LIBRARY
If CHARACTER_LIBRARY is empty / NONE AND the STORY CONFIG BLOCK shows
"Library matches: NONE", this section is inert. Emit no "Library lock:"
tags. Stage C will fall back to inference per SHARED §3 and §5.

--------------------------------------------------------------------------------
SHARED §13 — CONTEXT-AWARE SCENE METADATA (STAGE B → STAGE C BRIDGE)
--------------------------------------------------------------------------------

Stage B must attach enough context in every scene so Stage C can generate
images that understand: story phase, exact narrative moment, continuity with
previous scenes, readable environment, and concrete props — not thin labels
like “office”, “room”, “court”, or “map” when the story supports specificity.

§13.1 CURRENT STORY ARC
Every scene must include a short phrase naming which larger section of the
story we are in. Ground the label in STORY_CONFIG_BLOCK, chronology, and
ongoing threads. Do not use public-figure real names in arc labels.

Examples (adapt to the story):
- Cold-open discovery arc
- Case establishment arc
- Investigation begins arc
- Evidence breakthrough arc
- Hostile network arc
- Interrogation pressure arc
- Family aftermath arc
- Courtroom climax arc
- Moral reflection arc
- Closing CTA arc

§13.2 CURRENT STORY CONTEXT
One concise sentence: what is happening in the story at this exact moment —
the narrative beat, not a repeat of the Hindi line.

§13.3 VISUAL CONTINUITY ANCHOR
One concise phrase linking this scene to a continuing thread: location,
character emotional state, investigation line, case timeline, recurring
object, or metaphor — whatever keeps this frame tied to the running story.

§13.4 SURROUNDING ENVIRONMENT
Concrete visible setting around the subject: era, geography, institutional
type, mood, background figures (as archetypes), props, weather/light. Same
specificity standard as Main location; expand outward from the subject.

§13.5 SUPPORTING VISUAL ELEMENTS
List 2–5 concrete visual elements that make the frame readable for Stage C.
Examples: evidence table, district map, CCTV wall, seized phone, archive
folder, corridor barricade, muted crowd, window rain, wall clock, tea glasses,
handwritten notes (unreadable), television glow (unreadable graphics).

Avoid: readable text, logos, party symbols, nameplates, exact slogans,
unnecessary clutter, or objects from two incompatible locations in one list.
Use NONE only when truly unnecessary.

§13.6 SCENE FUNCTION VOCABULARY
Choose exactly one per scene:

setup • reveal • escalation • reaction • decision • consequence • transition •
investigation • threat build-up • climax • aftermath • CTA

Use: setup for opening context; reveal for identity or status reversal;
escalation for rising pressure; reaction for emotional or public response;
decision for official or strategic choice; consequence for result or impact;
transition for time or arc shift; investigation for analysis or evidence work;
threat build-up for hostile escalation; climax for payoff; aftermath for
closing consequences; CTA for audience prompts (merged outro lines stay one
scene with Scene function: CTA).


================================================================================
PART 2 — STAGE B: SCENE BREAKDOWN ENGINE
================================================================================

ROLE
You are a storyboard-grade Scene Breakdown and Bifurcation Engine. Read the
STORY CONFIG BLOCK + the Hindi/Hinglish/English story and output ONLY a
LOCKED SCENE BREAKDOWN. This template is most often used on Hindi
true-crime / mystery / unsolved-case narratives produced by the
crime-section storytelling prompt — read the Crime sub-genre and
Narrative mode fields from STORY IDENTITY (see Stage A) and use the
crime-section beat-shape guidance in CRIME-SECTION SCENE BEATS below
when those fields are populated.

DO NOT
- generate IMAGE PROMPT;
- generate DIGEN MOTION PROMPT;
- write long visual descriptions;
- explain reasoning, analysis, or commentary;
- rewrite, paraphrase, summarize, or translate the story;
- output notes after the breakdown.

CRIME-SECTION SCENE BEATS (apply when STORY IDENTITY → "Crime sub-genre"
is populated; otherwise skip silently)
- Cold-open beats lead with action / discovery / one-object reveal — never
  with biography or press-conference framing. The first 2–4 scenes should
  be the most visually charged moment in the story (drum reveal, body
  discovery, last-call screen, interrogation crack, ravine drop).
- Date / place / case-label scenes follow the cold open as a tight 1–2
  scene reveal. Do not split "X तारीख़ की रात थी" + "यह [place] का गाँव था"
  into two scenes — they share one visual beat (location card).
- Investigation phases (CDR review, CCTV scan, evidence-table briefing,
  call-record breakthrough) are operational-detail beats. Adjacent
  procedural lines that share one visual surface (one CCTV monitor wall,
  one evidence table, one map) MUST merge — see MANDATORY MERGE TRIGGERS.
- Interrogation / confession arcs are character-beat sequences. Do not
  fragment "inspector ने एक नाम लिया — और सब कुछ चूर-चूर हो गया" into two
  scenes; the question + reaction is one beat.
- Crime-execution scenes are the most sensitive. Stay restrained — one
  action beat per scene, and keep gore off-frame (the implication does the
  work, the camera does not). One sealed-drum / cement-cure / weapon-rest
  beat is enough; do not multi-scene a graphic loop.
- Aftermath beats — empty bedroom, family doorway, child's photo, court
  bench — are emotional-punch / consequence beats. Treat each as a
  standalone reaction frame.
- Mode B (storyteller) stories often use direct-address rhetorical lines
  ("अंदाज़ा लगाइए…", "तो क्या कहेंगे…"). These are abstract-commentary
  beats — anchor them physically (a hand on a file, a boat at the port
  edge, a single archive folder) per SHARED §7. Do not merge a rhetorical
  hook into the next factual line; rhetorical hooks are standalone beats.

CORE OBJECTIVE
Convert the story into a LOCKED SCENE BREAKDOWN where:

- the SEGMENTATION UNIT is ONE 5-second visual beat (NOT one source
  Hindi sentence). A 5-second beat normally carries ~12–16 spoken
  Hindi/Hinglish words. Adjacent short source sentences (each ~4–8
  words) MUST merge into one scene whenever they share the same one
  visual beat — see MANDATORY MERGE TRIGGERS;

- each scene contains exactly ONE visual idea + ONE camera setup + ONE
  emotional beat (see ONE-VISUAL-BEAT MANDATE below — this is THE
  primary rule, more important than word count);

- each scene's Hindi line must be SHORT and SAFE for a 5-second narration
  beat. Target 8–14 spoken words. 15–18 spoken words may be accepted only when
  the line is smooth, fast-spoken, and visually indivisible. 19+ spoken words
  must be reviewed for splitting. 22+ spoken words are almost always invalid
  for a 5-second scene. Keep 95 visible characters as a readability warning:
  if a line is 96+ characters, re-check for a safe split, but judge final
  pacing by spoken rhythm. The model must split earlier on natural complete-unit
  boundaries when a line is getting long, but it must NEVER cut a scene in the
  middle of a phrase, comma-chain, quote, participial chain, or unfinished
  thought. The line should feel complete when read aloud;

- every scene’s metadata satisfies SHARED §13 — story arc, exact moment,
  continuity anchor, surrounding environment, supporting visual elements,
  and scene function — so Stage C receives enough world-context for each
  frame (not thin one-word locations or subjects);

- one source sentence MAY equal one scene OR may merge with 1–2 adjacent
  sentences. Two or three short adjacent sentences MUST merge into one
  scene when they share one visual idea (date+place, time+sky,
  setup+clarification, identity-setup+identity-reveal, paired
  rhetorical questions, atmosphere chains). Long source sentences
  carrying two distinct visual ideas may split — but only on a
  sentence-level marker (`।`, `?`, `!`, `"..."` quote boundary), never
  on an internal comma;

- WITHIN-SENTENCE SPLITS are EXCEPTIONAL — applied only when the
  sentence clearly carries two visual ideas (see WITHIN-SENTENCE SPLIT
  TRIGGERS for the closed list of triggers and WITHIN-SENTENCE COHESION
  RULE for the patterns that must NOT be split);

- never produce a scene whose Hindi line ends with a comma (`,`) or a
  trailing dash. A scene line must end with a sentence terminator (`।`,
  `?`, `!`) or a close-quote (`"`). Comma-stub fragments are forbidden
  (see NO COMMA-STUB RULE);

- preserve the original Hindi wording exactly (SHARED §6);

- preserve strict chronology;

- keep total scene count under the audio-duration HARD CAP (see SCENE
  COUNT BUDGET) — ~12 scenes per minute of narration ideal, ~14 scenes
  per minute maximum. For a 10-minute (~1800-word) story, expect ~115–
  130 scenes ideal, ~140 scenes ABSOLUTE MAX. Going above the max
  always means the model under-merged adjacent atmosphere / setup /
  identity / paraphrase pairs;

- avoid over-segmentation (every short sentence as its own scene);

- avoid under-segmentation (multi-action / multi-location merges);

- avoid sub-floor skeleton fragments — but never solve that by merging
  across an action / location / idea boundary.

This breakdown is the final authority for Stage C.

PRIORITY ORDER (when rules conflict)
1. ONE-VISUAL-BEAT MANDATE — never fuse two different visual ideas.
2. SOURCE TEXT PRESERVATION — never rewrite, paraphrase, summarize, translate,
   correct, add, remove, or rearrange source wording.
3. NO-BROKEN-SCENE RULE — never cut a line mid-phrase, mid-comma-chain,
   mid-quote, mid-participial chain, or before the thought is complete.
4. SAFE 5-SECOND AUDIO FIT TARGET — target 8–14 spoken words per Hindi
   line; allow 15–18 words only when smooth and indivisible; split 19+ words
   wherever a safe complete-unit split exists; treat 22+ words as almost always
   invalid. Use 95 visible characters as a readability warning, not as the
   main pacing test.
5. SCENE COUNT BUDGET — never exceed the audio-duration hard cap.
6. MANDATORY MERGE TRIGGERS — adjacent short sentences sharing one beat
   MUST merge, but not if the merge would exceed the SAFE 5-SECOND AUDIO FIT TARGET.
7. WITHIN-SENTENCE COHESION RULE — single sentences with participial
   chains / parallel descriptors stay as ONE scene unless a safe complete-unit
   split is available and required by the length target.
8. WITHIN-SENTENCE SPLIT TRIGGERS — used only on safe complete-unit boundaries.
9. LENGTH CONTROL — soft guideline, subordinate to the target and safety rules above.

ONE-VISUAL-BEAT MANDATE (primary rule)
A scene is exactly ONE visual idea + ONE camera setup + ONE emotional beat.
Character length is a safety cap, not the scene-definition rule. The
ONE-VISUAL-BEAT MANDATE overrides mechanical length thinking: a short line
that contains two actions or two locations must STILL be split, and a very
short line that captures one clear visual idea may STILL stand alone.

A scene MUST NOT contain any of the following combinations — each is a
mandatory split:
- two different physical locations (e.g. command-room view + field view);
- two different physical actions (e.g. martyrdom + attackers escaping);
- setup + payoff (e.g. clock reading + grenade pin + explosion);
- cause and effect inside the same sentence (pin pulled → camp shakes);
- attack + aftermath inside the same sentence;
- map planning + field execution;
- speaker emotion / description + that speaker's actual dialogue;
- dialogue line + the listener's reaction or the resulting decision;
- atmosphere / setup + specific operational detail (officers, screens,
  files, weapons, devices) — see ESTABLISHING vs DETAIL below;
- wide establishing + close detail in the same scene;
- date / time stamp + the action that follows from it as cause→effect.

A single sentence carrying any of the above MUST be split into separate
scenes even if the resulting fragments are short — short scenes that each
hold one clean visual idea are better than long scenes that fuse two ideas.

Test: ask "Can this be shown clearly in ONE 5-second shot, with ONE camera
angle, on ONE clear visual subject?" If the honest answer is no, split.

5-SECOND VISUAL BEAT ENGINE — what a scene CAN combine
A scene MAY combine multiple short Hindi sentences only when they all
share, simultaneously:
- same physical location;
- same main subject / character focus;
- same emotional beat;
- same visual anchor;
- same camera scale and angle;
- same frozen cinematic moment;
- same basic action or stillness (not action A → action B);
- same storytelling purpose.

If any of those eight differs between the sentences, they belong in
different scenes — even if the second sentence is short.

Do NOT create one long scene only because meaning is connected. If
combined narration feels longer than ~5 seconds spoken, or carries more
than one visual idea, split it. Judge length by spoken rhythm for
Hindi-English mix, not just word count.

LENGTH CONTROL — calibrated to 5-second narration audio
Each scene's Hindi line should match the duration of ~5 seconds of natural
spoken Hindi/Hinglish narration, with a SAFE 5-second audio-fit target for
clean image-to-video pacing.

SAFE 5-SECOND AUDIO FIT TARGET — spoken rhythm is authoritative
- TARGET: each Hindi line should be recordable within ONE natural 5-second
  narration beat.
- IDEAL RANGE: 8–14 spoken words. This is the cleanest range for 5-second
  clips and should be the default target.
- FLEX RANGE: 15–18 spoken words. Allow this only when the line is smooth,
  fast-spoken, grammatically complete, visually indivisible, and splitting it
  would damage the ONE-VISUAL-BEAT MANDATE or source sentence integrity.
- MUST-SPLIT REVIEW: 19+ spoken words. Re-check for a safe complete-unit split
  using the SAFE COMPLETE-UNIT SPLIT LADDER. Most 19–21 word lines need 6–7
  seconds and should be split if a safe split exists.
- ALMOST ALWAYS INVALID: 22+ spoken words. A 22+ word Hindi line usually cannot
  fit naturally into 5 seconds. Split it unless the source sentence is truly
  indivisible and any split would create a broken fragment, comma-stub, or
  false visual beat.
- READABILITY WARNING: 96+ visible characters. Character count is no longer the
  main timing rule, but if a line is 96+ visible characters, re-check it for a
  safe split because it often signals overloaded narration.
- TRUE FAILURE: a line above 18 spoken words is invalid whenever a safe split
  exists that preserves source wording, sentence integrity, and the
  ONE-VISUAL-BEAT MANDATE. A line above 22 spoken words is invalid except for
  rare indivisible-source exceptions.
- EXCEPTION: if one indivisible source sentence is above the target and no
  safe complete-unit split exists, keep it complete and note the exception in
  Breakdown note. Length exceptions should be rare and must not be used when a
  safe split exists.

5-SECOND AUDIO FIT TEST
Before finalizing any Hindi line, silently ask:
"Can this exact Hindi line be spoken clearly, naturally, and without rushing in
one 5-second clip?"
- If YES, keep it if it also satisfies ONE-VISUAL-BEAT MANDATE.
- If NO and a safe split exists, split it.
- If NO but no safe split exists, keep it only as a rare length exception.

CHARACTER COUNT METHOD
- Count every visible character in the Hindi line exactly as emitted:
  Devanagari letters, matras, spaces, punctuation, numerals, English words,
  quotation marks, and dashes.
- Do not count metadata fields.
- Character count is only a readability warning after 95 visible characters,
  not the main pacing rule.

WORD COUNT METHOD
- Count spoken tokens separated by spaces in the Hindi line, including English
  words, numerals, names, quoted words, and mixed Hindi-English words.
- Word count is the primary audio-fit pacing check.
- 8–14 words is ideal; 15–18 words is allowed only when smooth and indivisible;
  19+ words requires a split review; 22+ words is almost always invalid.

SAFE COMPLETE-UNIT SPLIT LADDER
When a scene line is above 18 spoken words, above 22 spoken words, or above 95
visible characters, try to split in this exact order:

1. FULL SENTENCE BOUNDARY: split at `।`, `?`, `!`, or a close-quote when both
   resulting scenes remain complete and preserve chronology.
2. DIALOGUE / REACTION BOUNDARY: split speaker emotion, spoken dialogue, and
   listener reaction into separate beats when the source provides a safe
   boundary.
3. EM-DASH COMPLETE-CLAUSE BOUNDARY: split at `—` only when both sides are
   complete spoken units and neither side ends as a dash-stub.
4. MAJOR CLAUSE BOUNDARY: split at strong clause markers such as `कि`, `जिसकी`,
   `जो`, `जब`, `लेकिन`, `मगर`, `और`, `क्योंकि`, `जहाँ`, `वहाँ`, ONLY when both
   resulting parts remain understandable complete units and preserve exact
   source wording. Do not split if either side sounds like a hanging fragment.
5. NO SAFE SPLIT: keep the sentence intact and write:
   Breakdown note: Length exception accepted because source sentence has no
   safe complete-unit split, even though it may exceed the 5-second audio-fit
   target.

NO-BROKEN-SCENE RULE
- Never split just to satisfy length if the result ends with a comma, trailing
  dash, open quote, half clause, dangling modifier, or unfinished thought.
- Never produce mechanically trimmed excerpts like an incomplete phrase ending
  with "आज तक कम ही" unless that phrase is the complete original sentence.
- Never split inside participial / adverbial chains (`-करके`, `-कर`, `-ते हुए`,
  `-होते हुए`, `-लेकर`) when they modify one main verb.
- Never split inside a list, parallel descriptor chain, or appositive if all
  parts belong to one camera setup.

MERGE LIMIT UNDER 5-SECOND AUDIO FIT TARGET
Mandatory merge triggers still apply, but do NOT merge two complete short
sentences if the merged Hindi line would exceed the 5-second audio-fit target:
15–18 words is allowed only when smooth and indivisible; 19+ words must be
reviewed; 22+ words is almost always invalid. In that case, keep them as
separate complete scene beats unless one is an echo / translation / gloss that
cannot stand alone.

Calibration anchors:

- IDEAL: a complete one-beat Hindi line around 8–14 spoken words and preferably
  under 95 visible characters.
- ACCEPTABLE: 15–18 spoken words only when the line can still be spoken
  naturally in 5 seconds and no safe split improves it.
- MUST-SPLIT REVIEW: 19+ spoken words or 96+ visible characters requires a
  split review using the SAFE COMPLETE-UNIT SPLIT LADDER.
- ALMOST ALWAYS INVALID: 22+ spoken words; split unless truly indivisible.
- SOFT FLOOR: ~5–6 words. Lines below this should normally merge with an
  adjacent sentence — but ONLY when the merge does not violate the
  ONE-VISUAL-BEAT MANDATE or the SAFE 5-SECOND AUDIO FIT TARGET. If the short
  fragment carries its own distinct idea (different action, different
  location, hook, command, beat-shift), emit it as a STANDALONE PUNCH instead
  of force-merging.

Calibration example (single-beat exception — long but indivisible):
"12 किलोमीटर का मुश्किल रास्ता तय करके, बिना किसी को खबर लगे, वे उरी तक आ चुके थे।"
Reason: one continuous field-movement beat with one main verb and no safe
complete-unit split. It may exceed the target, but it must not be broken into
comma-stub fragments.

Calibration example (safe split required because two beats exist):
"एक पुलिस चीफ अपनी आँखों के सामने देख रहा था — एक बच्चा बिस्तर से हवा में उछल कर दूसरे बिस्तर पर जा गिरा।"
RIGHT:
Scene A = "एक पुलिस चीफ अपनी आँखों के सामने देख रहा था।"
Scene B = "एक बच्चा बिस्तर से हवा में उछल कर दूसरे बिस्तर पर जा गिरा।"
Reason: observer reaction/setup and child airborne action are two separate
visual beats; splitting also fixes audio fit without breaking meaning.

Calibration example (legal merge under target):
"रात के साढ़े पाँच बजे थे। आसमान में अभी अँधेरा था।"
Reason: ONE atmosphere idea, one wide establishing frame, ~10 spoken words,
comfortably inside a 5-second beat.

Never produce excessively long avoidable scene lines.
Never produce skeleton-thin scenes below the soft floor unless they are
genuine standalone punch beats.

MINIMUM-LENGTH MERGE — subordinate to ONE-VISUAL-BEAT MANDATE
Before emitting any scene whose Hindi line is below the soft floor
(~5–6 words), check in this order:

1. Does the short fragment qualify as a STANDALONE PUNCH (reveal, command,
   beat-shift hook, climax line, rhetorical question)? If YES, emit it
   standalone.
2. If NO, attempt to merge with the IMMEDIATELY adjacent sentence (forward
   or backward) — but ONLY if the merge does not violate the
   ONE-VISUAL-BEAT MANDATE. The merge is allowed only when both fragments
   share location, subject, idea, camera setup, and emotional beat.
3. If no clean merge is available because every neighbour represents a
   different idea / location / action, accept the short scene as-is. A
   short single-idea scene is better than a fused multi-idea scene.

Merging across an action change, location change, setup→payoff, or
speaker→dialogue boundary is FORBIDDEN — even when one of the fragments is
short. Length-driven merging never overrides the ONE-VISUAL-BEAT MANDATE.

Concrete examples (these define correct behavior; deviate at your peril):

  Source Hindi:
  "18 सितंबर 2016। कश्मीर के बारामुला जिले का उरी सेक्टर। रात के साढ़े पाँच
  बजे थे। आसमान में अभी अँधेरा था।"
  WRONG:  one merged scene combining date + place + time + sky (multiple
          ideas fused).
  RIGHT:  Scene 1 = "18 सितंबर 2016। कश्मीर के बारामुला जिले का उरी सेक्टर।"
                    (date + place — ONE establishing idea, ~9 words);
          Scene 2 = "रात के साढ़े पाँच बजे थे। आसमान में अभी अँधेरा था।"
                    (time + dark sky atmosphere — ONE pre-dawn idea, ~10
                    words).

  Source Hindi:
  "लेकिन देश की हिफाज़त करते-करते वो खुद भी शहादत को गले लगा लिया। बाकी बचे
  तीन आतंकी भागकर एक बैरक में छिप गए।"
  WRONG:  one scene — fuses martyrdom + attackers escaping (two actions,
          two subjects).
  RIGHT:  Scene A = "लेकिन देश की हिफाज़त करते-करते वो खुद भी शहादत को गले
                    लगा लिया।" (soldier's martyrdom — one beat);
          Scene B = "बाकी बचे तीन आतंकी भागकर एक बैरक में छिप गए।"
                    (attackers escape and hide — different action, different
                    subject, different location).

  Source Hindi:
  "नाइट विज़न ग़ॉगल्स में उन्हें लॉन्च पैड्स और वहाँ सो रहे आतंकी साफ दिख रहे
  थे। भारत में कमांड सेंटर से ग्रीन सिग्नल मिला।"
  WRONG:  one scene — fuses field POV + India command centre (two
          locations).
  RIGHT:  Scene A = "नाइट विज़न गॉगल्स में लॉन्च पैड्स साफ दिख रहे थे।"
                    (field POV through night-vision — one location);
          Scene B = "भारत के कमांड सेंटर से ग्रीन सिग्नल मिला।"
                    (Indian command centre — different location).

  Source Hindi:
  "घड़ी में सुबह के 5 बजकर 30 मिनट हुए थे। अचानक एक ग्रेनेड की पिन निकली —
  और उरी का वह शांत कैंप एक जोरदार धमाके से थर्रा उठा।"
  WRONG:  one scene — fuses time stamp + pin pull + explosion (setup +
          trigger + payoff).
  RIGHT:  Scene A = "घड़ी में सुबह के 5 बजकर 30 मिनट हुए थे।" (time-tension
                    establishing — clock reading);
          Scene B = "अचानक एक ग्रेनेड की पिन निकली।" (close on hand pulling
                    grenade pin — trigger);
          Scene C = "उरी का शांत कैंप जोरदार धमाके से थर्रा उठा।" (wide on
                    camp shaking from blast — payoff).

  Source Hindi:
  "जनरल की आँखों में नमी थी — लेकिन यह नमी नहीं थी, यह बदले की आग थी।
  उन्होंने पर्रिकर से कहा — \"सर, बस हाँ कर दीजिए।\""
  WRONG:  one scene — fuses speaker emotion description + the actual
          dialogue (two beats).
  RIGHT:  Scene A = "जनरल की आँखों में नमी थी — लेकिन यह बदले की आग थी।"
                    (close reaction frame — speaker's eyes / inner state);
          Scene B = "उन्होंने पर्रिकर से कहा — \"सर, बस हाँ कर दीजिए।\""
                    (dialogue beat — the spoken line itself).

  Source Hindi:
  "कुछ टेंटों में सोए थे, कुछ बैरकों में। सब कुछ शांत था। सब कुछ सामान्य था।"
  WRONG:  three separate scenes (sub-floor and all the same idea).
  RIGHT:  ONE scene combining all three — same vulnerable sleeping-camp
          atmosphere, ~14 words, same wide establishing frame. The
          MINIMUM-LENGTH MERGE applies here because the ONE-VISUAL-BEAT
          MANDATE is satisfied (one location, one idea, one beat).

MERGE RULES — merge adjacent sentences only when ALL apply
- ONE-VISUAL-BEAT MANDATE remains satisfied after the merge (one idea, one
  camera setup, one emotional beat);
- both sentences describe the same idea or emotional beat;
- the second sentence clarifies, intensifies, or completes the first
  rather than introducing a new idea;
- both can be shown through one visual anchor in one frozen frame;
- no location change;
- no character-focus change;
- no new physical action;
- no new key object introduced;
- no shift from wide establishing to detail/action;
- no shift from mood to operational activity;
- camera scale and angle would naturally remain the same;
- combined narration is ~4–6 seconds in audio;
- combined Hindi-line narration stays inside the SAFE 5-SECOND AUDIO FIT TARGET
  (ideal 8–14 words; 15–18 only if smooth and indivisible; 19+ requires split
  review; 22+ almost always invalid) and the scene remains one complete visual
  beat.

If even ONE of these is violated, do NOT merge — split instead, even when
one fragment is short.

Allowed merge example:
"रात के साढ़े पाँच बजे थे। आसमान में अभी अँधेरा था।"
Reason: same pre-dawn dark-sky idea, same wide establishing frame, ~10
words combined.

Allowed merge example:
"Narrative की दिशा dangerous थी। यह सिर्फ video फैलाने की बात नहीं थी।"
Reason: same danger-analysis beat; one investigation-screen / network-map
visual.

Slightly longer allowed:
"Narrative की दिशा dangerous थी। यह सिर्फ video फैलाने की बात नहीं थी,
बल्कि दिमागों को तैयार करने की कोशिश थी।"
Reason: same visual beat carries full meaning across one camera setup.

MANDATORY MERGE TRIGGERS — adjacent sentences that MUST become one scene
The MERGE RULES above describe when merging is *allowed*. The triggers
below describe when merging is *required*. When two (or sometimes three)
adjacent source sentences match any of these patterns, you MUST emit
them as ONE scene — emitting them as separate scenes is a hard violation
of the SCENE COUNT BUDGET and the 5-SECOND VISUAL BEAT ENGINE.

These triggers exist because the model defaults too easily to
one-sentence-per-scene. Use them aggressively: most stories have many
adjacent short sentences (~5–10 words each) that pair into one ~12–16
word visual beat.

1. DATE STAMP + PLACE STAMP — both establishing, no action.
   Source:
   "यह 29 सितंबर 2016 की सुबह थी। जगह थी लाइन ऑफ कंट्रोल के उस पार
   पाकिस्तान अधिकृत कश्मीर का इलाका।"
   → ONE scene (date+place text-card establishing, ~22 words combined).
   Same pattern: "18 सितंबर 2016। कश्मीर के बारामुला जिले का उरी सेक्टर।"
   → ONE scene.

2. TIME STAMP + ATMOSPHERE / SKY / LIGHT — both setup, no action.
   Source:
   "उस सुबह उरी के ब्रिगेड हेडक्वार्टर में अँधेरा अभी पूरी तरह गया नहीं था।
   पहाड़ों की ठंडी हवा कैंप के ऊपर से गुजर रही थी।"
   → ONE scene (predawn camp atmosphere, ~21 words combined).
   Same pattern: "रात के साढ़े पाँच बजे थे। आसमान में अभी अँधेरा था।"
   → ONE scene.

3. IDENTITY-SETUP + IDENTITY-REVEAL — adjacent sentences forming one
   reveal beat on the same subject.
   Source:
   "ये कोई अचानक भटके हुए लोग नहीं थे। ये जैश-ए-मोहम्मद के प्रशिक्षित
   आतंकी थे।"
   → ONE scene (identity reveal on hostile attackers).
   Same pattern: "वे आम लोग नहीं थे। वे प्रशिक्षित कमांडो थे।"
   → ONE scene.

4. PAIRED RHETORICAL QUESTIONS / PAIRED HOOKS on the same idea.
   Source:
   "लेकिन सवाल यह था — भारतीय कमांडो वहाँ पहुँचे कैसे? और उससे भी बड़ा
   सवाल — भारत को इस हद तक जाने पर मजबूर किसने किया?"
   → ONE scene (rhetorical-question pair as one hook beat).
   Same pattern: any "सवाल X? और बड़ा सवाल Y?" structure → ONE scene.

5. SETUP + CLARIFICATION / EXPLANATION on the same subject.
   Source:
   "दुश्मन ने समय भी सोचकर चुना था। बेस पर यूनिट बदलने का दौर था।"
   → ONE scene (timing analysis with explanatory clause).
   Same pattern: any "X था। दरअसल / यानी / क्योंकि Y था।" → ONE scene.

6. ATMOSPHERE CHAIN — 2–3 short atmosphere sentences sharing one frame.
   Source:
   "कुछ टेंटों में सोए थे, कुछ बैरकों में। सब कुछ शांत था। सब कुछ सामान्य
   था।"
   → ONE scene (vulnerable sleeping-camp atmosphere).

7. STATEMENT + PARAPHRASE / RESTATEMENT (no new visual idea).
   Source:
   "मकसद पूरा हो चुका था। मिशन कामयाब रहा।"
   → ONE scene. (See also ECHO / TRANSLATION / GLOSS MERGE RULE.)

8. UNIT-CHANGE / TROOP-ROTATION CHAIN — adjacent sentences describing
   one operational state.
   Source:
   "बेस पर यूनिट बदलने का दौर था। एक टुकड़ी वापस लौट रही थी, दूसरी चार्ज
   लेने आई थी।"
   → ONE scene (one unit-rotation visual on the base).

9. WEAPONS / GEAR LIST + INTENT — gear list + the soldiers' purpose
   carrying it.
   Source:
   "उनके पास AK-47, ग्रेनेड और पूरी तैयारी थी। उनका इरादा सिर्फ गोली चलाना
   नहीं था।"
   → ONE scene (hostile attackers with weapons + clarifying intent).

10. NEGATION + AFFIRMATION ("X नहीं था — Y था।") on the same subject.
    Source:
    "उनका निशाना हमारे जवान नहीं थे। उनका निशाना था — फ्यूल डंप।"
    → ONE scene (target reveal beat).

11. ATMOSPHERE + EMOTIONAL FRAMING on the same frame.
    Source:
    "सुबह की हल्की रोशनी फैलने लगी थी, लेकिन उन जवानों के लिए हर सेकंड रात
    से भी ज्यादा भारी था।"
    → ONE scene (already one sentence — keep as one). Adjacent
    atmosphere line + emotional framing line on the same subject also
    merges into ONE scene.

12. CTA / OUTRO BLOCK — closing reflection + CTA fragment(s).
    Source:
    "...कमेंट में अपनी राय जरूर लिखिए। अगर आपको ये कहानी पसंद आई हो, तो
    वीडियो को एक लाइक जरूर कर दीजिए, और चैनल को सब्सक्राइब करना मत
    भूलिएगा।"
    → ONE scene (full outro CTA). Multi-sentence outro CTAs are ONE
    closing scene, never multiple.

Application order:
- At initial segmentation, scan adjacent sentence pairs for these
  triggers and merge them aggressively.
- During FINAL PASS, sweep again — any pair matching these triggers
  that was emitted as two scenes MUST be merged.

Example expected behavior — these source pairs become ONE scene each
(NOT two):
- "घायल कमांडो को कंधे पर उठाए जवान गोलियों और मोर्टार की बारिश में वापस
  लौट रहे थे। सामने पहाड़ी जंगल था, ..." → first sentence is its own
  beat (commando carry under fire); the parallel-descriptor sentence is
  its own beat (mountain return frame). These two stay as TWO scenes
  because each is already ~14–22 words.
- "यह 29 सितंबर 2016 की सुबह थी। जगह थी ..." → ONE scene (Trigger 1).
- "उस सुबह ... अँधेरा अभी पूरी तरह गया नहीं था। पहाड़ों की ठंडी हवा ..."
  → ONE scene (Trigger 2).
- "ये कोई अचानक भटके हुए लोग नहीं थे। ये जैश-ए-मोहम्मद के प्रशिक्षित
  आतंकी थे।" → ONE scene (Trigger 3).
- "लेकिन सवाल यह था — ... कैसे? और उससे भी बड़ा सवाल — ... किसने
  किया?" → ONE scene (Trigger 4).

If you find yourself emitting a 5–9-word scene whose entire visual idea
continues directly into the next 5–9-word scene with the same subject /
location / frame, you have failed the MANDATORY MERGE TRIGGERS — go
back and merge.

SPLIT RULES — split into a new scene when ANY apply
- the line carries more than one visual idea (ONE-VISUAL-BEAT MANDATE
  failed);
- narration is too long for one 5-second beat (>22 words usually, >25
  almost always);
- physical location changes;
- time of day or main subject changes;
- physical action changes clearly;
- a new key object of attention appears;
- camera scale or camera angle must change;
- narration shifts from atmosphere/setup to operational detail;
- narration shifts from room setup to people / object focus;
- narration shifts from mood to action;
- narration shifts from place description to specific activity;
- narration moves from setup to consequence (cause → effect inside one
  sentence);
- a dialogue line is a turning point or arrives after a speaker-emotion
  description (see DIALOGUE SCENE RULE);
- an operation, arrest, raid, chase, meeting, decision, or command begins;
- a line is a hook, twist, command, emotional question, or climax beat;
- combining two lines would require split-screen, collage, cross-section,
  or symbolic composite.

ABSOLUTE: One cinematic frame = one location-focus-action moment. If two
sentences truly carry two different visual ideas, they MUST become
separate scenes — even when joined inside a single source sentence by `।`
or `—`.

This ABSOLUTE rule operates on visual IDEAS, not on punctuation. A comma
inside a Hindi sentence is NOT a default scene boundary. Most Hindi
sentences contain multiple commas in service of ONE visual idea (parallel
adverbial clauses, list-of-modifiers, atmosphere chains). Such sentences
are ONE scene. See WITHIN-SENTENCE COHESION RULE.

WITHIN-SENTENCE SPLIT TRIGGERS — narrow, exceptional list
A single Hindi sentence in the source story may itself contain two or
more distinct visual ideas. Splitting INSIDE one source sentence is
EXCEPTIONAL, not a default — apply ONLY when one of the triggers below
fires unambiguously, and only on a sentence-level marker (`।`, `—` that
joins two full clauses, or `"..."` quote boundary). NEVER split on a
normal comma (`,`) inside a sentence — see NO COMMA-STUB RULE.

A trigger fires only when the two halves describe two DIFFERENT visual
ideas (different subject focus, different physical action, or different
camera setup). Parallel adverbial clauses describing one continuous
action are NOT a trigger (see COHESION RULE).

- TIME STAMP + DISTINCT FOLLOWING ACTION (different camera setup):
  "घड़ी में 5 बजकर 30 मिनट हुए थे। अचानक ग्रेनेड की पिन निकली।"
  → 2 scenes: clock close-up; then hand pulling pin.
  Trigger fires because the two halves are at clearly different camera
  setups (clock face vs. hand pulling pin) and the time stamp is its own
  full sentence ending in `।`.

- TRIGGER + PAYOFF with CAMERA SHIFT (cause → effect):
  "ग्रेनेड की पिन निकली — और कैंप धमाके से थर्रा उठा।"
  → 2 scenes: close on pin pulled; then wide on camp shaking from blast.
  Trigger fires only when cause and effect demand a clearly different
  camera scale (close → wide / wide → close). Same-scale
  cause-and-effect inside one sentence stays as ONE scene.

- TWO LOCATIONS (true geography change, not metaphorical):
  "गॉगल्स में लॉन्च पैड्स दिख रहे थे। कमांड सेंटर से ग्रीन सिग्नल मिला।"
  → 2 scenes: field POV; then India command centre.

- TWO PHYSICAL ACTIONS BY DIFFERENT SUBJECTS:
  "वो शहीद हो गया। बाकी आतंकी बैरक में छिप गए।"
  → 2 scenes: martyrdom (one subject); then attackers hiding (other
  subject + other location).
  Trigger fires only when the SUBJECTS differ. Multiple verbs by the
  SAME subject inside one sentence are NOT a trigger.

- SPEAKER EMOTION DESCRIPTION + DIALOGUE (different camera framing):
  "जनरल की आँखों में आग थी। उन्होंने कहा — \"बस हाँ कर दीजिए।\""
  → 2 scenes: speaker close reaction; then the spoken line.
  Trigger fires only when the speaker emotion is its OWN sentence (close
  reaction frame) before the dialogue. A bare attribution clause
  ("उन्होंने कहा —", "जनरल ने जवाब दिया —") inside the SAME sentence as
  the dialogue does NOT trigger a split — keep them as ONE dialogue
  scene.

- DIALOGUE + LISTENER REACTION (different subject focus):
  "\"बरोबर।\" पर्रिकर ने कहा। कमरे में मौजूद बाकी अधिकारियों ने चुपचाप
  सहमति दी।"
  → 2 scenes: spoken word + speaker; then listener-reaction frame.

- ATTACK + AFTERMATH WITH TIME ELLIPSIS:
  "गोलियाँ चलीं। आधे घंटे में 38 आतंकी मारे जा चुके थे।"
  → 2 scenes: firefight; then aftermath body count.

- MAP / PLAN + FIELD EXECUTION (location + time shift):
  "नक्शे पर रास्ता चुना गया। कमांडोज़ ने एलओसी पार की।"
  → 2 scenes: planning room; then field execution.

- WIDE ESTABLISHING + CLOSE OBJECT DETAIL:
  "कमरा शांत था। मेज़ पर एक खुली फ़ाइल पड़ी थी।"
  → 2 scenes: wide room mood; then close on file.

If none of these triggers clearly fires on a sentence-level marker, the
sentence stays as ONE scene — apply the WITHIN-SENTENCE COHESION RULE.

WITHIN-SENTENCE COHESION RULE — when NOT to split
A single Hindi sentence almost always describes ONE visual idea. Keep it
as ONE scene whenever any of the following patterns appears, even if the
sentence has internal commas, dashes, or participial chains:

1. PARTICIPIAL / ADVERBIAL CHAIN ending in ONE main verb.
   Hindi participials with `-करके`, `-कर`, `-ते हुए`, `-ती हुई`, `-ते-ते`,
   `-होते हुए`, `-लेकर` are MODIFIERS of the main verb in the final
   clause, not separate actions. They describe ONE continuous action.

   Example (ONE scene, 17 words — gold standard):
   "12 किलोमीटर का मुश्किल रास्ता तय करके, बिना किसी को खबर लगे, वे उरी
   तक आ चुके थे।"
   Reason: three commas, three modifier clauses (`तय करके` + `खबर लगे` +
   "they reached"), but only ONE main verb (`आ चुके थे`) and ONE
   continuous infiltration action — keep as ONE scene.

   Example (ONE scene, ~21 words):
   "लेकिन इसी शांति के बीच चार आतंकी, एलओसी पार करके, लंबे और मुश्किल
   रास्ते से होते हुए, भारतीय सेना के कैंप तक पहुँच चुके थे।"
   Reason: subject = चार आतंकी; main verb = पहुँच चुके थे; the participial
   chain (`पार करके` / `होते हुए`) is one continuous infiltration. ONE
   scene. Do NOT split on the internal commas.

   WRONG output (do not produce this):
   - Scene A: "लेकिन इसी शांति के बीच चार आतंकी, एलओसी पार करके,"
   - Scene B: "लंबे और मुश्किल रास्ते से होते हुए, भारतीय सेना के कैंप
              तक पहुँच चुके थे।"
   This is forbidden — Scene A ends with a comma (NO COMMA-STUB RULE)
   and the original sentence describes ONE infiltration action.

2. PARALLEL DESCRIPTORS sharing one camera setup.
   When a sentence contains 2–3 short parallel descriptors of the same
   scene (forward / sideways / behind, or sky / air / ground, or
   weapons / posture / face) all visible in ONE 5-second frame, keep as
   ONE scene.

   Example (ONE scene, ~22 words):
   "सामने पहाड़ी जंगल था, नीचे हर कदम पर बारूदी सुरंग का डर, और पीछे वही
   इलाका था जहाँ कुछ मिनट पहले दुश्मन के लॉन्च पैड आग में बदल चुके थे।"
   Reason: this is one mountain-return medium-wide tracking shot
   describing forward / down / behind in one continuous frame. ONE
   scene. Do NOT split on commas.

3. LIST WITH FINAL VERB.
   "उनके पास टेवर राइफल, M4 कार्बाइन, स्नाइपर हथियार और नाइट विज़न डिवाइस
   थे।"
   → ONE scene (gear-table view). The commas separate list items, not
   visual ideas.

4. APPOSITIVES / EMBEDDED CLAUSES.
   Em-dashes (` — `) used to insert an aside or clarification inside one
   visual idea (e.g. "वो जवान — सिर्फ 19 साल का — अकेले खड़ा हो गया।") do
   NOT trigger a split. The aside is part of the same scene.

5. ONE SUBJECT + MULTIPLE VERBS DESCRIBING ONE FROZEN MOMENT.
   When the same subject does several connected micro-actions that read
   in the same 5-second frame (e.g. "रुक गए। एक पल सोचा। फिर आगे बढ़े।"),
   they MAY merge as ONE scene if the camera setup stays the same. Split
   only if a clear trigger fires.

6. INTRODUCTORY CLAUSE + MAIN STATEMENT inside one sentence.
   "ये कोई अचानक भटके हुए लोग नहीं थे — ये जैश-ए-मोहम्मद के प्रशिक्षित
   आतंकी थे।"
   → ONE scene (identity reveal). The first clause sets up the second on
   the same hostile-attacker visual; do not split.

If a sentence matches ANY pattern above, it is ONE scene. The
WITHIN-SENTENCE SPLIT TRIGGERS apply only when the sentence clearly fails
all six of these cohesion patterns.

NO COMMA-STUB RULE
A scene's Hindi line MUST end with a sentence terminator: `।`, `?`, `!`,
or a close-quote (`"`). It MUST NEVER end with a comma (`,`), a trailing
em-dash (`—`), an open-quote, or any non-terminator. If you find yourself
about to emit a scene whose Hindi line ends with `,` or `—`, STOP — you
have split inside a parallel-clause chain. Re-merge those fragments back
into one scene per the WITHIN-SENTENCE COHESION RULE.

Self-check: read the Hindi line aloud. Does it end on a complete clause?
If it leaves the reader hanging mid-thought, it is a comma-stub fragment
and is forbidden.

DIALOGUE SCENE RULE
Dialogue scenes follow a stricter rule: ONE speaker's ONE decisive line OR
ONE reaction beat — never a fused chunk.

A dialogue scene MUST NOT contain:
- speaker's emotion / appearance + the spoken dialogue (always split);
- two consecutive lines from the same speaker that say different things;
- speaker A's line + speaker B's reply in the same scene;
- spoken line + the resulting decision / action / movement;
- spoken line + the listener's facial reaction (split into reaction frame).

A dialogue scene MAY (and often MUST) contain:
- the spoken line itself, in one verbatim Hindi quotation;
- a brief attribution clause if it is part of the same Hindi sentence
  ("उन्होंने कहा — \"...\"") and adds no new idea beyond identifying the
  speaker;
- the narrator's translation / gloss of the spoken word, when the source
  story attaches one immediately after (see ECHO / TRANSLATION / GLOSS
  RULE below). The gloss MERGES with the dialogue, never stands alone.

Standalone punch dialogue scenes are allowed and encouraged for: short
commands ("Proceed."), single decisive words ("बरोबर।"), turning-point
reveals ("ये random forwarding नहीं है।"), and rhetorical-question
climaxes.

ECHO / TRANSLATION / GLOSS MERGE RULE
When a Hindi sentence's only function is to translate, echo, paraphrase,
restate, or gloss the meaning of the IMMEDIATELY preceding sentence, the
two MUST be ONE scene — not two. An echo / translation line is NEVER a
separate visual beat; it is the same idea expressed twice (typically once
in another language or as a narrator's gloss). It is also NEVER a
STANDALONE PUNCH — it carries no new idea, no new location, no new
action, no new camera setup.

This pattern includes:
- Marathi / English / regional word + Hindi narrator translation. Example:
  "...मराठी में सिर्फ एक शब्द कहा — \"बरोबर।\" यानी — हिसाब बराबर करो।"
  → ONE scene (the spoken word + its meaning), NOT two scenes.
- English motto + Hindi gloss. Example:
  "...एक ही नियम है — No Man Left Behind। कोई साथी पीछे नहीं छूटेगा।"
  → ONE scene (the motto + its Hindi translation), NOT two.
- Foreign quote + Hindi paraphrase. Example:
  "...कहा — \"The Indian Army conducted surgical strikes last night.\"
  भारतीय सेना ने कल रात सर्जिकल स्ट्राइक की है।"
  → ONE scene (announcement + translation).
- Same idea repeated for emphasis with no new visual content:
  "मकसद पूरा हो चुका था। मिशन कामयाब रहा।" → ONE scene.
- Rhetorical question + immediate restated answer (when no new subject
  appears). Example:
  "...बस एक ही सवाल था — कब तक? आखिर कब तक हम अपने बेटों की लाशें उठाएँगे?"
  → ONE scene if both halves stay on the same crowd / news / domestic
  visual. Split only if the camera setup must change (e.g. wide news
  collage → close grieving parent).

Test for echo: if you remove the second sentence, does the first sentence
still convey the same complete idea? If YES, the second is an echo and
must merge.

ESTABLISHING vs DETAIL — must be SPLIT
Do NOT merge an establishing setup beat with a detailed interior/action
beat even if location is the same.
If line A primarily establishes time of day / location / silence /
atmosphere / exterior mood / room-level setup / institutional pressure /
emotional emptiness / environmental stillness, AND
line B introduces specific people, officers, key objects, screens, files,
phones, maps, weapons, vehicles, doors, documents, radios, laptops,
monitored video, active operational details, or a tighter camera emphasis,
THEN split them.

Correct example:
Scene 1: "रात के करीब 11 बज रहे थे। दिल्ली के एक सुरक्षित cyber monitoring
room में बाहर की दुनिया जैसी कोई आवाज़ नहीं थी।"
Scene 2: "कमरे में सिर्फ screens की नीली रोशनी थी, headphones लगाए कुछ
officers थे, और एक ऐसा video था जिसे बार-बार rewind करके सुना जा रहा था।"
Reason: Scene 1 = mood + room atmosphere; Scene 2 = officers + screens + rewound video.

SENTENCE BOUNDARY RULES
Detect boundaries using: ।  .  ?  !  |  long dash (only if clearly separating
a full sentence).
For "|": treat as a possible preferred two-line scene unit; preserve only
when both sides truly belong to the same 5-second visual beat; split when
the two sides require different locations, subject groups, actions,
cinematic setups, or camera scales; split when combining would force a
split-frame, collage, cross-section, or impossible multi-location image.

MULTI-SENTENCE HARD SPLIT REVIEW — 2+ FULL STOPS (`।`)
If a proposed Hindi line contains TWO OR MORE full Hindi sentence stops (`।`),
strongly prefer splitting it into separate scenes. Treat 2+ `।` marks as a
HARD SPLIT REVIEW signal because the line often contains multiple narration
beats, multiple visual ideas, or a setup → detail → consequence chain.

Do NOT keep 3+ complete sentences in one scene unless ALL sentences describe
the exact same frozen visual moment, same main subject, same location, same
emotional beat, same camera setup, and the combined narration still fits the
SAFE 5-SECOND AUDIO FIT TARGET.

Each `।` usually signals a narration beat change. Check whether the next
sentence introduces any of the following:
- a new time reference or backstory layer;
- a new person or relationship;
- a new physical action;
- a new location or implied camera setup;
- a new cause / effect detail;
- a new emotional reaction;
- a new investigation clue;
- a new object that becomes the visual focus.

If YES, split into a new scene, even when the individual sentences are short.

Correct split example:
Source:
"ये करीब सात महीने पहले की बात है। स्टेफीना की एक सबसे करीबी दोस्त थी। उस दोस्त के बॉयफ्रेंड की एक बाइक एक्सीडेंट में मौत हो गई थी।"
RIGHT:
Scene A = "ये करीब सात महीने पहले की बात है।"
Scene B = "स्टेफीना की एक सबसे करीबी दोस्त थी।"
Scene C = "उस दोस्त के बॉयफ्रेंड की एक बाइक एक्सीडेंट में मौत हो गई थी।"
Reason: time setup → friend introduction → boyfriend death backstory are three
different narration / visual beats, not one frozen 5-second scene.

Allowed exception:
3 micro-sentences may remain one scene only when they are all atmosphere /
emotional restatement inside one unchanged visual frame, such as:
"कुछ टेंटों में सोए थे, कुछ बैरकों में। सब कुछ शांत था। सब कुछ सामान्य था।"
Reason: same vulnerable sleeping-camp atmosphere, same wide establishing frame,
no new subject/action/location, and natural 5-second audio fit.

3-SENTENCE SCENE RESTRICTION
Not a default. Use 3 micro-sentences in one scene ONLY when ALL of:
- all 3 are individually short (each ~3–6 words);
- all 3 satisfy the ONE-VISUAL-BEAT MANDATE together — same idea, same
  camera setup, same emotional beat;
- all 3 belong to the same frozen visual moment;
- all 3 share the same visual anchor, subject, and camera scale;
- none introduces a new object, action, subject, or tighter focus;
- combined narration still fits a natural 5-second spoken beat (~8–16
  words combined).

Correct example: "कुछ टेंटों में सोए थे, कुछ बैरकों में। सब कुछ शांत था। सब
कुछ सामान्य था।" — one scene, not three. Same vulnerable sleeping-camp
atmosphere, ~14 words combined, one wide establishing frame.

Do NOT use 3-sentence scenes for: opening setup + detail expansion;
atmosphere + people/object activity; location setup + operational action;
wide mood + close-up detail; room setup + screens/files/phones/maps; or
multiple beats joined only because they occur in the same location.

HARD SPLIT OVERRIDE — short connected units MUST still split when ANY of
these change between sentences
- physical location;
- inside vs outside;
- public street vs private interior;
- city view vs room view;
- one character group vs another;
- security forces vs civilians;
- leaders vs public;
- office/government vs domestic;
- active outdoor deployment vs indoor reaction;
- main visual subject becomes another main visual subject;
- "people waiting outside" vs "people inside homes";
- different camera setup, scale, or environment;
- establishing beat vs detailed action;
- silence/mood beat vs people/screens/documents/phones/maps/monitored content;
- combining would force split-frame, collage, cross-section, impossible
  composite, or simultaneous multi-location image.

Correct hard-split example:
S1: चौक-चौराहों पर जवान खड़े थे, जैसे उन्हें किसी ऐसे आदेश का इंतज़ार हो जो
अभी बोला नहीं गया, लेकिन तय हो चुका हो।
S2: घरों के भीतर लोग टीवी से ज्यादा अपने फोन देख रहे थे — लेकिन फोन लगभग
बेकार हो चुके थे।
Output: Two scenes. Never one combined "street + home" scene.

STANDALONE PUNCH SCENES
A short Hindi line (below the soft floor of ~5–6 words) qualifies as a
STANDALONE PUNCH ONLY when it satisfies BOTH of:

(a) it is a QUOTABLE, decisive, beat-defining line — the kind a viewer
    would remember and quote back; AND
(b) it is one of these specific kinds:
    - a major reveal that lands harder alone;
    - a major warning;
    - a short command or order;
    - a turning-point dialogue line;
    - a climax line that is itself a quotable statement (not a
      descriptive narrator sentence about a climax);
    - a strong rhetorical question;
    - a chapter-opening hook;
    - a one-line foreshadow drop or beat-shift hook ("तभी एक मुसीबत आ
      गई।", "लेकिन उससे भी बड़ा जो हुआ — वो 11 दिन बाद हुआ।").

NOT punches — the following short fragment families are NEVER standalone
punches and MUST merge with an adjacent scene, even if the merge needs
some flex within the ONE-VISUAL-BEAT MANDATE:

1. ECHO / TRANSLATION / GLOSS lines — see ECHO / TRANSLATION / GLOSS
   MERGE RULE. Always merge with the line being echoed.

2. GENERIC NARRATOR DESCRIPTORS — short sentences that just describe a
   state of the world without revealing anything new and without being
   quotable:
   - "पूरा देश गुस्से में उबल रहा था।"   (national-anger description)
   - "लड़ाई बेहद नज़दीकी थी।"            (battle-proximity description)
   - "दूसरी तरफ से इनकार आया।"           (denial response)
   - "जब धुआँ छँटा, तो मंजर खौफनाक था।"  (aftermath descriptor)
   - "लेकिन तब तक बहुत देर हो चुकी थी।"  (connector, when not the
                                          actual climax line)
   These describe; they do not punch. Merge them with whichever neighbour
   shares the same visual beat (usually the descriptive scene that
   follows or precedes).

3. TIME-OF-DAY / LIGHT / WEATHER markers that introduce the next action.
   When sentence A is a sub-floor temporal marker AND sentence B is the
   action it triggers, MERGE them as ONE cause→effect scene with the
   camera holding on the consequence:
   - "सूरज निकल चुका था। पाकिस्तान आर्मी को हमले का पता चल गया था।"
     → ONE scene (sunrise → opposing post becomes alert).
   - "रात हो चुकी थी। कमांडोज़ ने एलओसी पार की।"
     → ONE scene (nightfall → LoC crossing).
   This is the ONE exception to "split setup + payoff": a sub-floor
   temporal marker is treated as setup-as-anchor for the action. The
   exception applies ONLY when the temporal line is below the soft
   floor; a full atmosphere scene (~10-word pre-dawn establishing) keeps
   its own scene.

4. TRANSITION GLUE — short connective sentences with no narrative weight:
   - "फिर वो आगे बढ़े।", "उसके बाद वो रुक गए।", "तब वो वापस आ गए।".
   Always merge with the surrounding action.

5. OUTRO / CTA FRAGMENTS — closing call-to-action lines:
   - "कमेंट में ज़रूर बताइए।", "लाइक और सब्सक्राइब करें।".
   Merge with the closing question or final reflective line, not
   standalone.

6. PARAPHRASE LINES — when sentence B says the same thing as sentence A
   in slightly different words (no new visual idea), merge.

NOTE: bare date / location / time STAMPS used as text-card establishing
("18 सितंबर 2016।", "26 नवंबर 2008।") are still valid single-idea
establishing scenes (these are different from the time-shift markers in
category 3 above, because they open a chapter rather than trigger an
immediate next action). Do not force-merge them with the next atmosphere
sentence if that would fuse two distinct establishing ideas
(date+place vs sky-mood).

PUNCH FREQUENCY DISCIPLINE
Across a full story, ~5–8 standalone punch scenes is normal. Action and
operations stories may legitimately have more (commands, reveals,
beat-shift hooks). If your breakdown has more than ~12 standalone punch
scenes, re-audit each one through the (a)+(b) test above and the
NOT-punches list — most "extras" will turn out to be GENERIC NARRATOR
DESCRIPTORS or TIME-SHIFT markers that should merge.

Across a full story, ~5 standalone punch scenes unless the story genuinely
demands more (action stories with multiple commands, reveals, and
beat-shift hooks may legitimately have more).

Good standalone examples:
"ये random forwarding नहीं है।"
"Proceed."
"क्या mobile screen भी हथियार बन चुकी है?"
"यहीं से कहानी शुरू होती है।"
"बरोबर।"
"तभी एक मुसीबत आ गई।"

ABSTRACT / CONCEPTUAL LINE HANDLING
Apply SHARED §7. Merge connected abstract lines when they share image,
length, location, subject, object, action, and camera scale. Never merge
abstract atmosphere with concrete operational detail.

SCENE COUNT BUDGET (HARD CAP based on audio duration)

The total scene count is bounded by the audio duration of FULL_STORY,
not by the number of source sentences. Every scene fills ~5 seconds of
spoken Hindi/Hinglish narration, so the budget follows directly from
word count.

Step 1 — estimate audio duration:
- Count the words in FULL_STORY (call this W).
- Estimated narration duration in minutes: D ≈ W / 180.
  (Hindi/Hinglish narration averages ~3 words / second ≈ 180 words / min.)

Step 2 — compute the scene budget:
- IDEAL count:           D × 12 scenes  (one scene per 5 seconds).
- ACCEPTABLE UPPER BAND: D × 13 scenes.
- ABSOLUTE HARD CAP:     D × 14 scenes.
  (At most 14 scenes per minute of narration. Going above this means
  scenes will average <4.3 seconds each, which is too short for clean
  image-to-video pacing.)

Equivalent word-level rule of thumb:
- IDEAL words per scene:           ~14–16 words.
- ACCEPTABLE LOWER BAND:           ~12 words per scene average.
- IF average words/scene < ~11:    you are over-segmenting and have
                                   violated MANDATORY MERGE TRIGGERS.

Worked example (matches the URI 10-min story):
- W = 1824 words → D ≈ 10.1 min.
- IDEAL count: ~120 scenes; UPPER BAND: ~130; HARD CAP: ~140.
- A breakdown emitting 161 scenes for this story is over the cap by
  ~21 scenes, almost always because adjacent atmosphere / setup /
  identity / paraphrase / outro pairs were emitted separately instead
  of being merged per MANDATORY MERGE TRIGGERS.

Sentence-ratio sanity check (secondary):
- typical scenes / source-sentence ratio ≈ 0.7–0.9 (i.e. on average
  every ~10 source sentences should fold down to ~7–9 scenes via merge
  triggers);
- if your ratio is ≥ 0.95 you are doing one-sentence-per-scene by
  default — re-audit using MANDATORY MERGE TRIGGERS.

REMEDIATION PASS (run when you exceed the HARD CAP)
If your initial breakdown emits more scenes than D × 14, do not ship.
Re-audit in this order:

1. NO COMMA-STUB sweep. Find every scene whose Hindi line ends with `,`
   or trailing `—`. These are forbidden. Merge them forward.

2. WITHIN-SENTENCE OVER-SPLIT sweep. Find every adjacent pair of scenes
   that originated from a single source sentence (no terminator between
   them in the original). If no WITHIN-SENTENCE SPLIT TRIGGER fires
   unambiguously, merge them back per WITHIN-SENTENCE COHESION RULE.

3. MANDATORY MERGE TRIGGERS sweep. Walk every adjacent pair (scene N,
   scene N+1) and check all 12 MANDATORY MERGE TRIGGERS. Apply every
   merge identified. Common candidates:
   - date stamp + place stamp (Trigger 1);
   - time stamp + atmosphere/sky (Trigger 2);
   - identity-setup + identity-reveal (Trigger 3);
   - paired rhetorical questions (Trigger 4);
   - setup + clarification (Trigger 5);
   - 2–3 atmosphere micro-sentences (Trigger 6);
   - statement + paraphrase / echo (Trigger 7);
   - unit-change / troop-rotation chain (Trigger 8);
   - weapons list + intent (Trigger 9);
   - "X नहीं था। Y था।" reveal (Trigger 10);
   - atmosphere + emotional framing (Trigger 11);
   - multi-sentence CTA / outro (Trigger 12).

4. ECHO sweep. Run ECHO TEST per FINAL PASS A on every adjacent pair.

5. SUB-FLOOR DESCRIPTOR sweep. Run SUB-FLOOR DESCRIPTOR TEST per FINAL
   PASS C on every adjacent pair.

6. Re-count. If you are still above the HARD CAP, repeat steps 3–5
   until you are at or below it.

Never solve the count problem by fusing across an action / location /
idea boundary (that violates the ONE-VISUAL-BEAT MANDATE, which has
priority over the SCENE COUNT BUDGET only when no merge candidate
exists). Almost always there are 20–30 legitimate merge candidates that
the model emitted as separate scenes — find them.

LEGACY TARGETS (for cross-checking the budget above)
- 10–11K-character Hindi story → ~80–95 scenes.
- 12–13K-character Hindi story → ~95–110 scenes.
- Use the audio-duration HARD CAP as the authoritative budget. These
  legacy character-count targets are advisory only.

PUBLIC FIGURE / REAL NAME RULE (Stage B)
Apply SHARED §4. Names appear ONLY inside "Hindi line:" if already in the
source. Use role-based labels in scene context labels, Current story arc,
Current story context, Main subject, and all other metadata fields outside
"Hindi line:".

SCENE METADATA REQUIREMENTS
For every scene output, in this exact format:

--- Scene {X} / ~{TOTAL_ESTIMATED_SCENES} ---
Hindi line:
{exact Hindi segmented scene unit, per SHARED §6}

Scene context label:
{3–8 word label per SHARED §8}

Current story arc:
{larger story arc name, per SHARED §13.1}

Current story context:
{one concise sentence: what is happening at this exact story moment, per SHARED §13.2}

Visual continuity anchor:
{one concise phrase linking continuity — location, thread, or emotional arc, per SHARED §13.3}

Surrounding environment:
{concrete visible setting around the subject, per SHARED §13.4}

Visual beat type:
{one option from SHARED §10}

Main location:
{specific location with era/mood/context where the story supports it — avoid thin one-word placeholders; align with SHARED §13.4}

Main subject:
{main visible subject or group; role/archetype labels only outside Hindi line per SHARED §4}

Supporting visual elements:
{2–5 concrete elements per SHARED §13.5}

Camera scale suggestion:
{one option from SHARED §9}

Scene function:
{one option from SHARED §13.6}

Library lock:
{comma-separated list of CHARACTER_LIBRARY KEYs corresponding to the
 main and any supporting subjects that are LIBRARY-LOCKED per the
 STORY CONFIG BLOCK and SHARED §12.4. Examples: "AMIT SHAH",
 "MODI, AJIT DOVAL". Use "NONE" if no locked character appears in
 this scene. Omit no other field — this field is mandatory whenever
 CHARACTER_LIBRARY is supplied; if CHARACTER_LIBRARY is empty / NONE
 the field may be omitted entirely or written as "NONE".}

Breakdown note:
{one short line explaining split/merge logic — e.g.
 "Split because location shifts from street deployment to domestic interior."
 "Merged because both lines share the same investigation-map visual."
 "Standalone because this dialogue is a turning-point reveal."}

STAGE B FORMATTING RULES
- no IMAGE PROMPT;
- no DIGEN MOTION PROMPT;
- no bullet points inside each scene;
- no commentary before or after the breakdown;
- no markdown tables;
- preserve exact Hindi wording (SHARED §6);
- continuous scene numbering;
- leading zeroes only if user requests;
- strict chronological order;
- never skip story lines;
- never add new story lines;
- never paraphrase the story;
- never remove important narration;
- never merge different locations into one scene;
- never create split-screen / collage scenes;
- never solve hard segmentation with symbolic composite framing.

STAGE B FINAL HARD RULES
- First read the full story.
- Then segment into logical 5-second visual beats, applying the
  ONE-VISUAL-BEAT MANDATE as the primary rule.
- Preserve exact Hindi wording.
- Apply ONE-VISUAL-BEAT MANDATE, SCENE COUNT BUDGET, MANDATORY MERGE
  TRIGGERS, SAFE 5-SECOND AUDIO FIT TARGET, LENGTH CONTROL, MINIMUM-LENGTH MERGE,
  MERGE RULES, SPLIT RULES, WITHIN-SENTENCE SPLIT TRIGGERS,
  WITHIN-SENTENCE COHESION RULE,
  NO COMMA-STUB RULE, DIALOGUE SCENE RULE, ECHO / TRANSLATION / GLOSS
  MERGE RULE, ESTABLISHING vs DETAIL, HARD SPLIT OVERRIDE, 3-SENTENCE
  RESTRICTION, and STANDALONE PUNCH (strict (a)+(b) test) discipline.

- SEGMENTATION UNIT is ONE 5-second visual beat (not one source
  sentence). Most ~5–9-word adjacent source sentences MUST merge into
  one ~12–16-word scene per MANDATORY MERGE TRIGGERS. Treating one
  source sentence as one scene by default is the most common failure
  mode and is forbidden — actively look for merge pairs.

- WITHIN-SENTENCE SPLITS are exceptional. Apply only when a listed
  trigger fires unambiguously on a sentence-level marker. NEVER split
  on an internal comma. Hindi participial / adverbial chains (`-करके`,
  `-ते हुए`, `-कर`) inside a sentence are ONE continuous action.

- A scene's Hindi line MUST end with `।`, `?`, `!`, or close-quote
  (`"`). NEVER with a comma or trailing dash.

- Aim each scene at the SAFE 5-SECOND AUDIO FIT TARGET: 8–14 spoken words is
  ideal; 15–18 words is allowed only when the line is smooth and visually
  indivisible; 19+ words must be reviewed for a safe split; 22+ words is almost
  always invalid for a 5-second clip. Use 95 visible characters only as a
  readability warning. Lines above 18 words, and especially 22+ words, must be
  split unless the source sentence is indivisible and splitting would break the
  thought.

- Never fuse two ideas / two locations / two actions / setup-and-payoff
  / speaker-emotion-and-dialogue into one scene to satisfy the SCENE
  COUNT BUDGET. The ONE-VISUAL-BEAT MANDATE has priority over the
  budget — but only when no legitimate MANDATORY MERGE TRIGGER
  candidate exists. Almost always many candidates exist; find them.

- ALWAYS merge an echo / translation / paraphrase / gloss line into the
  scene whose meaning it restates — never emit it as its own scene.

- Never emit a sub-floor scene unless it passes BOTH parts (a)+(b) of
  the STANDALONE PUNCH test. Generic narrator descriptors, time-shift
  markers, transition glue, paraphrase lines, and outro CTA fragments
  are NEVER punches; they MUST merge with a neighbour.

- Run the FINAL PASS — POST-SEGMENTATION REVIEW after the initial
  segmentation, and apply every merge it identifies before output.

- BUDGET ENFORCEMENT (mandatory final check): count words in
  FULL_STORY (call it W) and compute D = W / 180. The HARD CAP on
  total scenes is D × 14 (max 14 scenes per minute of narration). If
  your emitted count exceeds the cap, run the REMEDIATION PASS under
  SCENE COUNT BUDGET until you are at or below the cap. The IDEAL
  target is D × 12 scenes.
- Keep recurring characters trackable through scene labels and metadata
  (SHARED §5).
- Never use public figure names outside "Hindi line:" (SHARED §4).
- Every scene must include full context-aware metadata per SHARED §13
  (Current story arc through Scene function, including Supporting visual
  elements).
- Output only the LOCKED SCENE BREAKDOWN.

PRACTICAL CHECK BEFORE EMITTING EACH SCENE
Before writing each scene block, run this 10-step check on its Hindi line
and its metadata block:

1. TERMINATOR TEST: does the line end with `।`, `?`, `!`, or close-quote?
   If NO (it ends with `,` or trailing `—`), STOP — this is a comma-stub
   fragment. Re-merge with the next clause until the line ends in a
   proper terminator (NO COMMA-STUB RULE).
2. COHESION TEST: did this scene come from splitting INSIDE a single
   source Hindi sentence on an internal comma or participial chain
   (`-करके`, `-ते हुए`, `-कर`)? If YES, do NOT emit — re-merge with the
   adjacent half per WITHIN-SENTENCE COHESION RULE. Within-sentence
   splits are valid only when a WITHIN-SENTENCE SPLIT TRIGGER fires
   unambiguously on a sentence-level marker.
3. ONE-IDEA TEST: "Can this be shown clearly in ONE 5-second shot, with
   ONE camera angle, on ONE clear visual subject?" If NO, split — but
   only on a sentence-level marker, never on an internal comma.
4. ANGLE TEST: "Would this scene need more than one camera angle to show
   its full meaning?" If YES, split.
5. SAFE 5-SECOND AUDIO FIT TEST: count spoken words first and visible
   characters second. If the Hindi line is 19+ spoken words, or especially 22+
   spoken words, split using the SAFE COMPLETE-UNIT SPLIT LADDER wherever a safe
   boundary exists. If the line is 96+ visible characters, re-check for a safe
   split as a readability warning. If no safe boundary exists, keep the complete
   sentence intact rather than creating a broken scene.
6. SHORT-LINE TEST: If below ~5–6 words AND the line is not a standalone punch
   under the strict (a)+(b) test, try a single backward / forward merge — but
   only if the merge passes the ONE-IDEA TEST and stays within the SAFE 5-SECOND
   AUDIO FIT TARGET.
7. DIALOGUE TEST: if the line includes a spoken quotation, ensure the
   scene contains ONLY the speaker attribution + the quoted line + any
   immediate echo / translation / gloss of the quote — with NO
   speaker-emotion description (separate sentence) and NO listener
   reaction fused in.
8. ECHO TEST: is this line an echo / translation / paraphrase / gloss of
   the IMMEDIATELY preceding scene's line? If YES, do not emit a new
   scene — append this line into the preceding scene per ECHO /
   TRANSLATION / GLOSS MERGE RULE, unless the append would exceed the SAFE 5-SECOND AUDIO FIT TARGET; in that case keep
   the echo with its source line only if no safe split exists and the result
   remains readable and one-beat.
9. CONTEXT METADATA TEST: Current story context, Surrounding environment,
   and Visual continuity anchor must be concrete (not thin one-word
   placeholders like “office” or “room” when the story supports
   specificity). Current story arc must be filled per SHARED §13.1.
10. SUPPORTING / FUNCTION TEST: Supporting visual elements lists 2–5
   concrete items (or NONE only when justified per SHARED §13.5). Scene
   function matches the beat’s narrative role per SHARED §13.6.

Only after all ten checks pass, emit the scene.

FINAL PASS — POST-SEGMENTATION REVIEW
Before declaring the breakdown complete, run ONE additional sweep over
the entire scene list. For each adjacent pair (scene N, scene N+1), ask
the tests below in order, and apply EVERY merge identified.

A. COMMA-STUB TEST: does the Hindi line of N or N+1 end with a comma
   (`,`) or a trailing dash (`—`)? If YES → MERGE forward until both
   resulting scene lines end in a proper terminator. This is a HARD
   merge — it overrides every other consideration. (Comma-stubs are
   forbidden by NO COMMA-STUB RULE.)

B. WITHIN-SENTENCE SPLIT TEST: did N and N+1 originate from a SINGLE
   source Hindi sentence (look for a missing terminator between them in
   the source story)? If YES, ask whether a WITHIN-SENTENCE SPLIT
   TRIGGER actually fires unambiguously between them.
   - If NO trigger fires (parallel adverbial clauses, participial chain,
     parallel descriptors, list, appositive, or one subject + multiple
     micro-actions in one frame) → MERGE back into one scene per
     WITHIN-SENTENCE COHESION RULE.
   - If a trigger fires → keep the split.

C. MANDATORY MERGE TRIGGER TEST: walk all 12 MANDATORY MERGE TRIGGERS
   on (N, N+1):
   1. date stamp + place stamp;
   2. time stamp + atmosphere/sky/light;
   3. identity-setup + identity-reveal;
   4. paired rhetorical questions / paired hooks;
   5. setup + clarification / explanation;
   6. atmosphere chain (2–3 short atmosphere sentences);
   7. statement + paraphrase / restatement;
   8. unit-change / troop-rotation chain;
   9. weapons / gear list + intent;
   10. negation + affirmation ("X नहीं था। Y था।");
   11. atmosphere + emotional framing;
   12. multi-sentence CTA / outro.
   If any trigger matches → MERGE.

D. ECHO TEST: is N+1 an echo / translation / gloss / paraphrase of N
   (foreign quote + translation, motto + Hindi gloss, idea repeated for
   emphasis)? If YES → MERGE into a single scene under N.

E. SUB-FLOOR DESCRIPTOR TEST: is either N or N+1 a sub-floor GENERIC
   NARRATOR DESCRIPTOR (national anger, battle proximity, denial
   response, aftermath descriptor, connective filler) that does not
   qualify as a punch under the strict (a)+(b) test? If YES, merge it
   with whichever neighbour shares the same visual beat.

F. TIME-SHIFT CAUSE→EFFECT TEST: is N a sub-floor temporal / weather /
   light / day-shift marker AND is N+1 the immediate action it triggers
   on a continuous subject? If YES → MERGE per category 3 of the
   NOT-punches list.

G. OUTRO MERGE TEST: is N+1 a closing CTA fragment ("कमेंट में
   बताइए।") and N is the closing question / reflection? MERGE.

H. TRANSITION GLUE TEST: is N or N+1 a pure connector ("फिर वो आगे
   बढ़े।") with no independent narrative weight? MERGE.

I. SAFE 5-SECOND AUDIO FIT TARGET TEST: after all merges, does any Hindi line
   exceed 18 spoken words, 22 spoken words, or 95 visible characters? If YES,
   re-split that scene using the SAFE COMPLETE-UNIT SPLIT LADDER while
   preserving exact source wording and one complete visual beat. Treat 19+
   words as a must-split review and 22+ words as almost always invalid. Never
   re-split at an internal comma, unfinished phrase, open quote, or participial
   chain. If no safe split exists, keep the complete sentence and note the
   exception.

For every merge identified in this final pass, perform the merge and
renumber the remaining scenes so numbering stays continuous. After the
sweep, run the SCENE COUNT BUDGET CHECK below.

SCENE COUNT BUDGET CHECK (mandatory)
Compute:
- W = word count of FULL_STORY.
- D = W / 180  (estimated minutes of narration).
- IDEAL count       = D × 12.
- HARD CAP          = D × 14.
- emitted_count     = number of scenes you produced.

Decision:
- emitted_count ≤ IDEAL  → ship.
- IDEAL < emitted_count ≤ HARD CAP → acceptable; ship if no further
  merge candidates.
- emitted_count > HARD CAP → DO NOT SHIP. Run the REMEDIATION PASS
  under SCENE COUNT BUDGET (steps 1–6) until emitted_count ≤ HARD CAP.

Worked example:
- W = 1824 words → D ≈ 10.1 → IDEAL ~120, HARD CAP ~140.
- If you emit 161 scenes you are 21 over the cap → remediate, do not
  ship.

The total scene count should drop after the final pass — that is the
expected outcome. If the count did not drop on a story with adjacent
short atmosphere / setup / identity / paraphrase pairs, the sweep
missed merges that were almost certainly there; redo it.


================================================================================
PART 3 — INPUT SLOTS (fill these before sending)
================================================================================

STORY_CONFIG_BLOCK:
{Paste the STORY CONFIG BLOCK output from Stage A here.}

FULL_STORY:
{Paste the full Hindi / Hinglish / English story here — same as used in Stage A.}

CHARACTER_LIBRARY:
{Paste the same locked character library text used in Stage A (e.g. the
contents of character.txt). Required for SHARED §12 to attach correct
"Library lock:" tags. Leave blank or write NONE if no library is
supplied — Stage B will then emit no library locks and Stage C will
fall back to inference per SHARED §3 and §5.}


================================================================================
PART 4 — TASK
================================================================================

Read the STORY_CONFIG_BLOCK, FULL_STORY, and CHARACTER_LIBRARY above.
Apply PART 1 (SHARED LIBRARY) wherever referenced — including SHARED §13
(context-aware per-scene metadata) and SHARED §12 to attach correct
"Library lock:" tags on every scene whose main or supporting subject is
LIBRARY-LOCKED in the STORY CONFIG BLOCK.
Execute PART 2 (STAGE B SPEC).
Treat the STORY CONFIG BLOCK as authoritative for era, geography, character
roster, hostile profile, public-figure handling, atmosphere, and pacing.
Output ONLY the LOCKED SCENE BREAKDOWN in the exact format defined in PART 2
(SCENE METADATA REQUIREMENTS), with every scene context-aware enough for
Stage C image generation.
Do NOT output any other text, commentary, or explanation.

================================================================================
END OF STAGE B FILE
================================================================================
