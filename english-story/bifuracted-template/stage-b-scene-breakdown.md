Yes — here is the **full corrected Stage B English version** with the exact automation-compatible placeholders:

```text
================================================================================
STORYBOARD PIPELINE — STAGE B: ENGLISH CONTEXT-AWARE SCENE BREAKDOWN ENGINE
Story Doctor Version — 5-Second Audio Fit + Character Lock Audit
================================================================================

HOW TO USE THIS FILE WITH CHATGPT

1. First, run Stage A and save its STORY CONFIG BLOCK output.
2. Open a new ChatGPT chat for Stage B.
3. Copy this ENTIRE file and paste it as your first message.
4. At the very bottom, fill in the input slots:
      STORY_CONFIG_BLOCK:  <-- paste Stage A output
      FULL_STORY:          <-- paste the full English story
      CHARACTER_LIBRARY:   <-- paste locked character library, or write NONE
5. Send.
6. ChatGPT must return ONLY the LOCKED SCENE BREAKDOWN.
7. Save that LOCKED SCENE BREAKDOWN — it is the input to Stage C.

PIPELINE POSITION

   English Story
      ↓
   Stage A — Story Config Engine
      ↓
   >>> Stage B — English Context-Aware Scene Breakdown Engine <<<
      ↓
   Stage C — Image + Motion Prompt Engine

================================================================================
PART 0 — DISPATCHER
================================================================================

ACTIVE STAGE: B

Execute ONLY Stage B.

Your job:
- Read STORY_CONFIG_BLOCK.
- Read FULL_STORY.
- Read CHARACTER_LIBRARY if supplied.
- Segment the English story into locked 5-second visual beats.
- Preserve the English line exactly.
- Add enough context metadata so Stage C can generate images that understand:
  current story scenario,
  surrounding environment,
  continuity,
  emotional state,
  story arc,
  recurring characters,
  locked characters,
  hostile actors,
  public-figure safety,
  concrete visual details.
- Attach Library lock tags wherever the scene subject matches, references, implies, recalls, or visually represents a locked character.
- Output ONLY the LOCKED SCENE BREAKDOWN.

Do NOT:
- generate image prompts;
- generate motion prompts;
- explain reasoning;
- add commentary before or after the breakdown;
- summarize the story;
- rewrite English lines;
- correct grammar;
- remove story lines;
- add new narration;
- output tables;
- output markdown explanations;
- output anything outside the locked scene breakdown.

================================================================================
PART 1 — AUTOMATION / CONTINUATION SAFETY
================================================================================

If FULL_STORY contains any of the following:

CONTEXT OVERLAP
PREVIOUS SCENE RANGE
AUTHORITATIVE CONTINUATION
RECAP
ALREADY-FILMED CONTEXT
or similar recap rails,

treat those parts as already-filmed context only.

Rules:
- Do not emit new Scene entries exclusively for overlap or recap text.
- Continue strict chronological narration from the authoritative new body.
- Do not duplicate scenes from the previous range.
- Do not insert extra LOCKED SCENE BREAKDOWN headings.
- Do not insert excerpt titles.
- Do not insert separator ribbons.
- Do not insert “END OF...” lines between Scene blocks.
- Keep output clean because automation may merge multiple Stage B slices into one file.

================================================================================
PART 2 — SHARED RULES AND STAGE B SPEC
================================================================================

--------------------------------------------------------------------------------
GLOBAL VISUAL STYLE LOCK
--------------------------------------------------------------------------------

Use this visual language implicitly when describing scene metadata:

2D digital animated illustration;
cinematic hand-drawn 2D matte painting;
clean hand-drawn line art;
flat cel shading;
documentary realism;
restrained stylisation;
historically grounded environments;
region-accurate faces;
muted documentary color palette;
readable composition;
strong foreground / midground / background logic;
no empty stage-like backgrounds.

Avoid:
photorealism;
ultra realism;
3D render;
CGI;
ray tracing;
global illumination;
lens flare;
bokeh;
depth of field blur;
glossy CGI;
hyper-detailed pores;
HDR realism;
neon colors unless the story era supports them;
watermark;
logo;
readable text overlay;
poster layout;
split-screen collage;
generic empty backgrounds.

Stage B does NOT generate image prompts, but its metadata must be strong enough for Stage C to create cinematic 2D image prompts.

--------------------------------------------------------------------------------
PUBLIC FIGURE AND NAME RULE
--------------------------------------------------------------------------------

Applies to:
politicians,
ministers,
prime-ministerial figures,
home-ministerial figures,
advisors,
military leaders,
intelligence chiefs,
public officials,
public commentators,
and any recognizable real public person.

ABSOLUTE RULE:
Real public-figure names may appear ONLY inside English line if the original source line already contains them.

Outside English line, never write:
- real public figure names;
- initials that clearly identify them;
- exact likeness instructions;
- readable nameplates;
- readable party symbols;
- readable official insignia;
- readable logos;
- exact real-person image instructions;
- identifying image-prompt language.

Outside English line, convert public figures into role-based archetypes.

Use examples like:
- senior national political strategist figure
- senior prime-ministerial figure
- senior home-ministerial figure
- senior national security strategist figure
- state chief-ministerial figure
- senior party organiser
- national security official
- senior opposition figure
- political analyst
- grassroots worker
- senior police investigator figure
- senior intelligence official figure
- senior military commander figure

Library lock IDs are allowed ONLY in the Library lock field as pipeline metadata.

Do not use Library lock IDs anywhere else.

Correct:

English line:
Amit Shah walked into the courtroom under a wall of cameras.

Main subject:
senior home-ministerial figure entering court under media pressure

Library lock:
CHAR_HOME_01

Incorrect:

Main subject:
Amit Shah entering court

Incorrect:

Scene context label:
Amit Shah Court Entry

Incorrect:

Supporting visual elements:
Amit Shah photo on wall

--------------------------------------------------------------------------------
HOSTILE ACTOR VISUAL MENACE
--------------------------------------------------------------------------------

A hostile actor means:
terrorist,
extremist,
radical handler,
hostile recruiter,
radical propagandist,
violent conspirator,
terror commander,
criminal operative,
handler,
suspect linked to hostile activity,
hostile network member,
or any figure clearly identified by the story as operationally dangerous.

When hostile actors appear:
- Scene context label must carry grounded threat language.
- Main subject must identify them as hostile actor / militant / criminal operative / radical handler / extremist propagandist as appropriate.
- Surrounding environment must support threat reading.
- Supporting visual elements must show operational pressure through grounded objects.
- Do not describe hostile actors as gentle, innocent, harmless, ordinary, soft, warm, saintly, charming, noble, heroic, or neutral.

Civilian separation rule:
Do NOT apply hostile coding only because of religion, ethnicity, nationality, beard, skullcap, shalwar kameez, hijab, mosque background, regional clothing, poverty, or migration status.

Only apply hostile coding when the story identifies the person or group as hostile, criminal, extremist, militant, radical handler, propagandist, violent conspirator, terror commander, operative, handler, or suspect linked to hostile activity.

Ordinary civilians must remain ordinary civilians.

Hostile-scene metadata should include:
- hardened body language;
- secretive posture;
- tense setting;
- suspicious device / file / bag / hidden object where supported;
- low-light or guarded environment where appropriate;
- clear separation from ordinary civilians.

--------------------------------------------------------------------------------
CHARACTER CONSISTENCY AND LIBRARY LOCKS
--------------------------------------------------------------------------------

If CHARACTER_LIBRARY is supplied, Stage B must propagate library locks.

Rules:
1. Identify each scene’s main subject and important supporting subjects.
2. Check STORY_CONFIG_BLOCK roster and CHARACTER_LIBRARY.
3. If a subject corresponds to a locked character, add the exact neutral character ID from the roster’s “Library reference key” field in:

Library lock:

4. Multiple IDs are comma-separated.
5. If no locked character appears, write:

Library lock:
NONE

6. Do not copy the character library body into the breakdown.
7. Do not paraphrase locked character descriptions.
8. Stage B only carries the neutral character ID.
9. Stage C will resolve the full appearance using CHARACTER_LIBRARY.
10. Do not invent new IDs.

Important:
If the story repeatedly refers to a locked character through pronouns, titles, roles, reputation, memory, strategy, or indirect references, still attach the correct Library lock.

--------------------------------------------------------------------------------
CRITICAL LIBRARY LOCK ENFORCEMENT
--------------------------------------------------------------------------------

This stage must work with ANY story and ANY supplied character library.

The character library may change from project to project.
Do not hard-code any specific person, public figure, politician, officer, criminal, victim, child, family member, journalist, analyst, hostile actor, or fictional character.

Instead:
- detect available neutral character IDs from CHARACTER_LIBRARY;
- read STORY_CONFIG_BLOCK roster;
- use “Library reference key” from Stage A;
- match scene subjects through names, aliases, roles, titles, pronouns, continuity, and visual implication.

A Library lock ID is pipeline metadata, not an image-prompt name.

Therefore:
- public figure names are still forbidden outside English line;
- real names are forbidden in Main subject, Current story context, Scene context label, Main location, Surrounding environment, Supporting visual elements, Camera scale suggestion, Scene function, and Breakdown note;
- but the exact neutral character ID is allowed and required inside Library lock when that locked character is visually present or clearly referenced.

MANDATORY LOCK PROPAGATION:
If a scene visually contains, references, implies, recalls, shows a photograph of, shows a younger version of, shows an older version of, shows from behind, shows in silhouette, shows on a screen, shows through a reflection, shows through a file/photo/news clipping, shows only a hand/face/back/profile, or describes the actions, emotions, reputation, history, strategy, memory, decision, public reaction, or consequence around any character present in CHARACTER_LIBRARY, the matching Library lock MUST be added.

Do not write Library lock: NONE when the scene clearly belongs to a locked character through any of these forms:
- direct name in English line;
- alias;
- surname;
- title;
- role;
- office;
- relationship;
- pronouns such as he, she, they, his, her, their, this man, that figure, the strategist, the officer, the leader;
- previous-scene continuity;
- phrases like protagonist, central figure, central strategist figure, senior leader figure, officer figure, investigator figure, criminal figure, child, mother, father, friend, victim, witness, handler, recruiter, analyst, or any role that Stage A maps to a locked character;
- younger version;
- older version;
- flashback version;
- future version;
- public photo;
- archive photo;
- portrait;
- screen image;
- memory image;
- silhouette;
- reflection;
- partial body detail.

If the English line contains a locked character’s exact name, alias, title, or clear role reference, Library lock MUST NOT be NONE.

If the scene’s Main subject or Supporting visual elements describe a locked character even without a real name, Library lock MUST NOT be NONE.

If two or more locked characters appear in the same visual beat, list all IDs:

Library lock:
CHAR_HOME_01, CHAR_PM_01

Only use Library lock: NONE when no locked character is visually present, directly referenced, indirectly referenced, or contextually implied in that scene.

--------------------------------------------------------------------------------
STORY-GENERIC CHARACTER MATCHING METHOD
--------------------------------------------------------------------------------

Before emitting each scene, silently perform this matching sequence:

1. Extract all available neutral character IDs from CHARACTER_LIBRARY.
2. Read STORY_CONFIG_BLOCK roster, aliases, public figure mappings, and character-library matches.
3. For the current scene, identify:
   - visible subjects;
   - implied subjects;
   - supporting subjects;
   - named subjects;
   - role-based subjects;
   - pronoun referents;
   - archive / screen / memory / silhouette subjects.
4. Match scene subjects against the current story’s library IDs using:
   - exact name in English line;
   - aliases;
   - titles;
   - role mapping from STORY_CONFIG_BLOCK;
   - previous-scene continuity;
   - current story arc;
   - pronoun chain from the last 1–3 scenes;
   - location/context continuity;
   - visual phrases such as younger version, older version, photo, silhouette, hand, face, back view, screen image, reflection, or memory.
5. If a match exists, write the matching neutral character ID in Library lock.
6. If multiple matches exist, write all matching IDs in stable story order.
7. If no match exists, write Library lock: NONE.

Do not invent new IDs.
Use only IDs that exist in CHARACTER_LIBRARY or are explicitly enumerated as library-locked in STORY_CONFIG_BLOCK.

If a scene seems to refer to a recurring character but the character is not in CHARACTER_LIBRARY, do not invent a lock.

Use:

Library lock:
NONE

--------------------------------------------------------------------------------
REQUIRED LOCK AUDIT BEFORE FINAL OUTPUT
--------------------------------------------------------------------------------

Before returning the LOCKED SCENE BREAKDOWN, scan every scene and reject these failures:

FORBIDDEN FAILURE 1:
English line contains a locked character name, but Library lock is NONE.

FORBIDDEN FAILURE 2:
Current story context, Visual continuity anchor, Main subject, or Supporting visual elements clearly describe a locked character, but Library lock is NONE.

FORBIDDEN FAILURE 3:
Main subject uses a generic archetype for a character that exists in CHARACTER_LIBRARY, but Library lock is NONE.

FORBIDDEN FAILURE 4:
Scene shows a younger/older version, photograph, screen image, reflection, silhouette, back view, partial hand/face/body detail, archive image, or memory image of a locked character, but Library lock is NONE.

FORBIDDEN FAILURE 5:
Two locked characters appear in one scene, but only one ID is listed.

FORBIDDEN FAILURE 6:
A public figure real name appears outside English line or outside Library lock.

FORBIDDEN FAILURE 7:
A Library lock ID appears outside the Library lock field.

FORBIDDEN FAILURE 8:
A scene uses Library lock: NONE when the previous 1–3 scenes make the pronoun subject clearly refer to a locked character.

If any failure is found, fix the scene before output.

Correct pattern:

Main subject:
senior role-based archetype figure standing under legal and media scrutiny

Library lock:
{MATCHING_CHARACTER_ID}

Incorrect pattern:

Main subject:
senior role-based archetype figure standing under legal and media scrutiny

Library lock:
NONE

The second pattern is wrong whenever the role-based archetype corresponds to a locked character in this story.

--------------------------------------------------------------------------------
SOURCE TEXT PRESERVATION
--------------------------------------------------------------------------------

The English line field carries the original English narration.

The English line must preserve the original wording exactly.

Allowed:
- segmenting the story into scene units;
- merging adjacent full sentences when they form one visual beat;
- splitting only at valid sentence-level boundaries when one line carries multiple visual beats.

Not allowed:
- paraphrasing;
- grammar correction;
- rewriting;
- translation;
- removing words;
- adding new words;
- changing names;
- changing tone;
- modernizing phrasing;
- simplifying language;
- changing punctuation unnecessarily.

Every English line must end with:
.  ?  !  or a close quote.

Never output an English line that ends with:
comma,
open dash,
trailing dash,
colon,
semicolon,
open quote,
or incomplete phrase.

If the original line is incomplete because of segmentation, extend or split at the nearest complete sentence boundary.

The only allowed modification is segmentation between scenes.

--------------------------------------------------------------------------------
CORE OBJECTIVE
--------------------------------------------------------------------------------

Convert FULL_STORY into a LOCKED SCENE BREAKDOWN.

Each scene must represent:
- one 5-second visual beat;
- one visual idea;
- one camera setup;
- one emotional or narrative beat;
- one grounded story-world context.

Stage B is not only a segmentation engine.
Stage B is also the context bridge for Stage C.

The main failure to avoid:
Do not output thin metadata that only says:
“office”,
“room”,
“court”,
“street”,
“political figure”,
“map”,
“analysts”,
“crowd”,
“man”,
“woman”.

Stage C needs to understand:
- where we are in the larger story arc;
- what is happening at this exact moment;
- what surrounding environment should be visible;
- what previous or continuing context this scene belongs to;
- which objects, background details, crowd mood, institutional setting, domestic setting, battlefield setting, media setting, campaign setting, court setting, border setting, military setting, intelligence setting, or political setting make the image understandable;
- what this scene does in the narrative: setup, reveal, escalation, reaction, decision, consequence, investigation, threat build-up, climax, aftermath, transition, or CTA.

The English line gives the narration.
The metadata gives the image-world.

--------------------------------------------------------------------------------
CONTEXT-AWARE METADATA RULE
--------------------------------------------------------------------------------

For every scene, metadata must answer:

1. Current story arc:
Which larger section of the story are we in?

2. Current story context:
What is happening in the story at this exact moment?

3. Visual continuity anchor:
What recurring location, emotional state, strategy thread, investigation thread, campaign arc, legal arc, battlefield arc, intelligence arc, media arc, crisis arc, or metaphor does this scene continue?

4. Main location:
Where exactly should this scene visually happen?

5. Main subject:
Who or what is visually central?

6. Supporting visual elements:
What concrete objects/background details make the scene readable?

7. Surrounding environment:
What should be visible around the subject?

8. Camera scale suggestion:
How should Stage C frame the image?

9. Emotional tone:
What should the frame feel like?

10. Scene function:
Why does this scene exist in the story?

Bad metadata:

Main location:
office

Main subject:
man

Surrounding environment:
room

Better metadata:

Main location:
late-night intelligence office under emergency pressure

Main subject:
senior intelligence officer studying a blurred surveillance photograph

Surrounding environment:
dim office lights, pinned regional maps, file stacks, secure phone, red-circled location markers, tense silence

Supporting visual elements:
surveillance photograph, secure phone, regional map, file stack, wall clock, desk lamp, unreadable notes

Scene function:
investigation reveal

--------------------------------------------------------------------------------
SCENE CONTEXT LABEL RULES
--------------------------------------------------------------------------------

Scene context label must be:
- 3 to 8 words;
- title-like;
- concise;
- file-name friendly;
- no quotes;
- no slashes;
- no punctuation overload;
- descriptive of role, setting, action, mood, threat, or object;
- not based on real names.

Never use a public figure’s real name in Scene context label.
Avoid all real personal names where possible.

Use role/archetype instead.

Weak:
Amit Shah Court Entry

Better:
Court Pressure Entry

Weak:
Modi Strategy Room

Better:
Prime-Ministerial Strategy Room

Weak:
Terrorist Planning

Better:
Hostile Network Planning

If a scene includes a hostile actor, do NOT use soft labels.
Use grounded threat language.

Weak:
Man Using Phone

Better:
Hostile Handler Phone Signal

Weak:
Religious Man Sitting

Better:
Radical Handler Closed Room

Only use hostile labels when the story identifies the actor as hostile.

--------------------------------------------------------------------------------
ABSTRACT / CONCEPTUAL LINE HANDLING
--------------------------------------------------------------------------------

Conceptual lines have no concrete subject or action.

Examples:
“The pressure was not new.”
“The silence felt different.”
“This was not just about one video.”
“The narrative had already started moving.”
“The real danger was hidden deeper.”

Do not split abstract lines automatically.

Merge short connected abstract lines when:
- the same image can represent both;
- combined length is not too long;
- there is no location change;
- there is no subject change;
- there is no object change;
- there is no action change;
- there is no camera-scale change.

Do NOT merge abstract atmosphere with concrete operational detail such as officers, screens, files, maps, devices, vehicles, raids, crowds, courtrooms, or command rooms.

For abstract lines, metadata must ground the visual in a physically believable cinematic frame.

Use grounded anchors:
- screens;
- maps;
- files;
- phones;
- hands;
- faces;
- corridors;
- streets;
- closed rooms;
- evidence tables;
- muted crowds;
- empty spaces;
- paused routines;
- silent offices;
- suspicious digital activity;
- command rooms;
- border landscapes;
- media cameras;
- legal files.

Never use:
fantasy symbolism;
swirling smoke metaphors;
surreal cross-sections;
split-screen composites;
floating icons;
abstract glowing graphics;
poster-like symbolism.

--------------------------------------------------------------------------------
5-SECOND AUDIO FIT RULE
--------------------------------------------------------------------------------

Each scene must fit roughly 5 seconds of spoken English narration.

Target English line length:
- normally 10–16 spoken words;
- 17–18 words allowed only if smooth and indivisible;
- 19+ words must be reviewed for split;
- 22+ words should only be used as a rare exception when splitting would damage meaning.

Each scene should represent:
- one visual idea;
- one emotional beat;
- one camera setup;
- one moment in the story;
- one grounded story-world context.

Do not solve scene count by creating long overloaded scenes.

Do not fuse:
- different locations;
- different actions;
- speaker + listener reaction;
- wide establishing + close object detail;
- mood + active operation;
- metaphor + literal scene if they require different visuals;
- court scene + map metaphor;
- public reaction + private planning;
- political pressure + ground operation;
- hostile actor planning + official reaction.

If one sentence is too long, split it at a natural punctuation boundary or phrase boundary while preserving exact wording.

If multiple very short sentences form one visual beat, merge them.

Example:

Weak over-segmentation:
Scene 1:
The room went silent.

Scene 2:
The map said enough.

Better if same visual beat:
The room went silent. The map said enough.

Scene function:
decision pressure

--------------------------------------------------------------------------------
SCENE COUNT BUDGET
--------------------------------------------------------------------------------

Estimate narration duration:

W = approximate word count of FULL_STORY.
D = W / 180.

Ideal scene count:
D × 12.

Hard cap:
D × 14.

If emitted scenes exceed hard cap:
- merge true same-beat candidates;
- merge CTA fragments;
- merge abstract clarification pairs;
- merge repeated contrast pairs;
- merge paraphrases;
- merge short atmosphere chains;
- merge role-ladder fragments when they are one montage idea.

Average words per scene should usually be around 12–16.

If average is below 11, over-segmentation is likely.
If many scenes exceed 18 words, under-segmentation is likely.

Scene count should be practical for Stage C.

Remember:
Stage C generates very long image prompts, so Stage B should not create unnecessary micro-scenes.

--------------------------------------------------------------------------------
MERGE / SPLIT DECISION RULE
--------------------------------------------------------------------------------

MERGE adjacent lines when:
- they share the same location;
- they share the same subject;
- they share the same camera setup;
- they share the same emotional beat;
- they are short;
- they are one rhetorical unit;
- they form one CTA;
- they form one metaphor;
- they form one same-beat explanation.

SPLIT lines when:
- the location changes;
- the subject changes;
- the action changes;
- the emotion changes sharply;
- the camera needs to move from wide to close-up;
- the line introduces a new clue;
- the line introduces a new threat;
- the line introduces a new decision;
- the line changes from narration to quote/dialogue;
- the line moves from abstract idea to concrete action;
- the line would exceed 18–20 spoken words.

Standalone lines should remain alone when they are:
- a reveal;
- a command;
- a hook;
- a climax beat;
- a rhetorical punch;
- a hard turning point;
- a quote;
- a decisive order;
- a final CTA question.

--------------------------------------------------------------------------------
METADATA DENSITY RULE
--------------------------------------------------------------------------------

Every scene must have rich enough metadata for Stage C.

Minimum quality standard:

Main location:
Must be specific, not generic.

Main subject:
Must describe role, body/action/state, and story relevance.

Supporting visual elements:
Must list concrete physical objects. Prefer 4–8 objects.

Surrounding environment:
Must describe atmosphere, architecture, crowd/emptiness, lighting, and story-world context.

Visual continuity anchor:
Must connect the scene to a recurring arc.

Camera scale suggestion:
Must guide Stage C clearly.

Emotional tone:
Must be specific, not just “serious”.

Breakdown note:
Must explain why the scene was split/merged and what Stage C must preserve.

Bad:

Main location:
room

Main subject:
officer

Supporting visual elements:
files

Better:

Main location:
secure late-night command room during intelligence review

Main subject:
senior intelligence official figure leaning over a red-marked regional map under time pressure

Supporting visual elements:
regional map, secure phone, file bundles, desk lamp, unreadable surveillance prints, wall clock, sealed folder

Surrounding environment:
closed institutional room with low greenish lighting, tense silence, half-finished tea cups, and officers waiting outside the glass partition

--------------------------------------------------------------------------------
OUTPUT FIELD DEFINITIONS
--------------------------------------------------------------------------------

Each scene must contain these exact fields:

Scene number:
Sequential scene number.

English line:
Exact source narration segment. Preserve wording.

Scene context label:
3–8 word concise visual label with no real public figure names.

Current story arc:
The larger story section this scene belongs to.

Current story context:
What is happening at this exact moment.

Visual continuity anchor:
What thread this scene continues.

Main location:
Specific physical setting.

Main subject:
Central visible subject using role-based archetype if needed.

Supporting visual elements:
Concrete objects and background details.

Surrounding environment:
The larger environment around the subject.

Camera scale suggestion:
Use one of:
extreme wide establishing shot
wide establishing shot
medium-wide shot
medium shot
over-shoulder shot
close-up
extreme close-up
low-angle shot
high-angle shot
aerial establishing shot
tracking-style frame
static documentary frame

Emotional tone:
The exact feeling of the scene.

Scene function:
Use one of:
setup
reveal
escalation
reaction
decision
consequence
transition
investigation
threat build-up
climax
aftermath
CTA

Library lock:
Neutral character ID(s), or NONE.

Breakdown note:
Brief production note explaining segmentation, continuity, or visual emphasis.

--------------------------------------------------------------------------------
PUBLIC-FIGURE ARCHETYPE EXAMPLES
--------------------------------------------------------------------------------

Use these patterns outside English line:

senior prime-ministerial figure with composed statesmanlike posture

senior home-ministerial figure under legal and media pressure

senior national security strategist figure reviewing intelligence material

senior police investigator figure studying evidence inside a closed office

senior military commander figure standing before a regional operations map

senior intelligence official figure listening to a secure phone update

grassroots political worker waiting in a crowded campaign backroom

political analyst figure looking at election maps in a media studio

Do not use public names outside English line.

--------------------------------------------------------------------------------
HOSTILE ACTOR METADATA EXAMPLES
--------------------------------------------------------------------------------

If source identifies the subject as hostile:

Scene context label:
Hostile Handler Signal

Main subject:
hardened hostile network handler watching a phone inside a dim closed room

Surrounding environment:
low-lit back room with closed shutters, cheap smartphone glow, folded paper, cloth bag, and tense secrecy

Supporting visual elements:
cheap phone, closed shutter, table edge, cloth bag, unreadable coded note, weak bulb, dusty wall

Emotional tone:
controlled menace and hidden operational pressure

If source identifies an ordinary civilian:

Scene context label:
Border Civilian Anxiety

Main subject:
ordinary border-area civilian waiting anxiously near a crowded checkpoint

Surrounding environment:
dusty border-side street with families, bags, police barricade, tired faces, and uncertain movement

Emotional tone:
fear, confusion, and civilian uncertainty

Do not hostile-code civilians unless the story identifies them as hostile.

--------------------------------------------------------------------------------
CTA / OUTRO HANDLING
--------------------------------------------------------------------------------

CTA lines should not be over-segmented.

If CTA lines are short and visually belong together, merge into one scene.

Weak output:

Scene 1:
Write your view in the comments.

Scene 2:
Like the video.

Scene 3:
Subscribe to Story Doctor.

Better output:

One scene:
Write your view in the comments. If this story made you think, like the video and subscribe to Story Doctor.

Scene function:
CTA

CTA metadata should create a clean end-card style documentary frame without readable text.

Main location:
dark documentary end-frame environment with symbolic story objects

Main subject:
final visual arrangement of story-related objects representing the central question

Supporting visual elements:
map, file folder, dim lamp, empty chair, muted background, symbolic object from story

Do not create a literal YouTube subscribe button or readable text.

--------------------------------------------------------------------------------
STORY DOCTOR BRAND RULE
--------------------------------------------------------------------------------

The channel name is:

Story Doctor

If the English line already contains the channel name, preserve it exactly.

If CTA appears in the source story and uses another channel name, preserve the English line exactly in English line, but do not repeat the wrong channel name in metadata.

In metadata, use:
Story Doctor brand CTA frame

Never introduce any other channel name in metadata.

Do not add CTA if it is not in the FULL_STORY.

Stage B segments what exists; it does not write new narration.

--------------------------------------------------------------------------------
FINAL PASS CHECKS
--------------------------------------------------------------------------------

Before output, run these checks:

1. Terminator check:
Every English line ends with period, question mark, exclamation mark, or close quote.

2. No comma-stub check:
No English line ends with comma, trailing dash, colon, semicolon, or incomplete phrase.

3. One-visual-beat check:
Every scene can be shown in one 5-second shot.

4. Context check:
Every scene has strong Current story context and Surrounding environment.

5. Generic metadata check:
No generic “office”, “room”, “court”, “map”, “street”, “man”, “woman”, or “crowd” if the story supports specificity.

6. Supporting elements check:
Every scene has useful concrete visual elements.

7. Library lock check:
Any locked recurring figure appearing by name, alias, role, title, pronoun, younger/older version, photograph, silhouette, screen image, reflection, hand, face, back view, memory image, archive image, symbolic representation, or supporting/background presence gets the correct Library lock.

8. Library NONE check:
Library lock: NONE is forbidden when the scene maps to any supplied CHARACTER_LIBRARY ID.

9. Public figure name check:
No real public figure name outside English line except neutral Library lock metadata.

10. Library ID placement check:
No Library lock ID appears outside the Library lock field.

11. CTA merge check:
Outro fragments are merged into fewer scenes unless they have distinct visual beats.

12. Metaphor check:
Metaphors are grounded in real scene-world visuals, not impossible split-location composites.

13. Scene count check:
Emitted count should be within D × 14 hard cap unless the story genuinely demands more.

14. Safe audio-fit check:
Every English line should ideally be 10–16 spoken words. 17–18 is allowed only when smooth and indivisible. 19+ must have a split review. 22+ needs a rare exception.

15. Multi-sentence check:
Any English line with 2+ sentence-ending punctuation marks must be reviewed. Keep together only when all sentences share the same frozen visual beat and still fit 5 seconds.

16. Pipe separator check:
Any source `|` marker must be reviewed as a preferred split point unless both sides are one visual beat.

17. Broken-fragment check:
No scene may end mid-thought, mid-quote, mid-participial chain, or mid-comma chain.

18. Establishing/detail check:
Atmosphere/setup scenes must not be fused with screens, files, phones, maps, officers, documents, weapons, vehicles, or active operational details.

19. Echo/gloss check:
Translation, paraphrase, repeated statement, or gloss lines must not become standalone scenes unless they introduce a genuinely new visual beat.

20. Standalone punch check:
Very short scenes must be true reveal/command/hook/climax/rhetorical punch beats. Otherwise merge if a clean same-beat neighbour exists.

21. Continuation/overlap check:
If FULL_STORY contains CONTEXT OVERLAP or recap text from a previous chunk, treat it as already-filmed context and do not emit duplicate scenes from it.

22. Output-cleanliness check:
Do not insert extra headings, excerpt titles, separators, “END OF” ribbons, commentary, or explanations between scene blocks.

23. Hostile actor softness check:
No hostile actor is described as gentle, innocent, ordinary, warm, harmless, saintly, soft, friendly, heroic, or sympathetic.

24. Civilian separation check:
No ordinary civilian is made threatening based only on religion, ethnicity, nationality, dress, beard, skullcap, hijab, poverty, or migration status.

25. Stage C readiness check:
Every scene must give Stage C enough context to create foreground, midground, background, lighting, camera, mood, continuity, and negative prompt logic.

If any failure is found, fix the scene before output.

--------------------------------------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------------------------------------

Return only:

LOCKED SCENE BREAKDOWN

Use exactly this format:

================================================================================
LOCKED SCENE BREAKDOWN
================================================================================

Scene 1

English line:
[exact story line]

Scene context label:
[...]

Current story arc:
[...]

Current story context:
[...]

Visual continuity anchor:
[...]

Main location:
[...]

Main subject:
[...]

Supporting visual elements:
[...]

Surrounding environment:
[...]

Camera scale suggestion:
[...]

Emotional tone:
[...]

Scene function:
[...]

Library lock:
[...]

Breakdown note:
[...]

Scene 2

English line:
[exact story line]

Scene context label:
[...]

Current story arc:
[...]

Current story context:
[...]

Visual continuity anchor:
[...]

Main location:
[...]

Main subject:
[...]

Supporting visual elements:
[...]

Surrounding environment:
[...]

Camera scale suggestion:
[...]

Emotional tone:
[...]

Scene function:
[...]

Library lock:
[...]

Breakdown note:
[...]

Continue until the full authoritative story body is covered.

Do not use tables.
Do not add explanation before or after.
Do not add image prompts.
Do not add motion prompts.

--------------------------------------------------------------------------------
QUALITY EXAMPLES
--------------------------------------------------------------------------------

Weak output:

English line:
The operation was risky.

Main location:
office

Main subject:
officers

Surrounding environment:
room

Better output:

English line:
The operation was risky because every route created a different kind of danger.

Scene context label:
Risky Route Decision

Current story arc:
planning room pressure before final decision

Current story context:
The officials understand that every possible route carries a different operational risk.

Visual continuity anchor:
command-room decision arc with red-marked routes and rising time pressure

Main location:
dim military command room with a regional map open on the table

Main subject:
senior officers studying red-marked routes under time pressure

Supporting visual elements:
regional map, route markers, secure phone, sealed file, wall clock, desk lamp, unreadable notes

Surrounding environment:
low-lit command room with tense officers, closed doors, pinned maps, and a silent atmosphere before a risky decision

Camera scale suggestion:
medium-wide shot

Emotional tone:
controlled tension and strategic pressure

Scene function:
decision

Library lock:
NONE

Breakdown note:
This line works as one visual beat because the danger is expressed through the command-room map and route risk.

================================================================================
PART 3 — INPUT SLOTS (fill these before sending)
================================================================================

STORY_CONFIG_BLOCK:
{Paste the STORY CONFIG BLOCK output from Stage A here.}

FULL_STORY:
{Paste the full Hindi / Hinglish / English story here — same as used in Stage A.}

CHARACTER_LIBRARY:
{Paste the same locked character library text used in Stage A for THIS story.
The character folder/library may change per story; Stage B must detect the
available neutral character IDs from the supplied library and propagate those exact IDs into
"Library lock:" whenever the matching character appears, is referenced, is
implied, or appears as a younger/older/photo/silhouette/screen/reflection/memory
version. Leave blank or write NONE if no library is supplied — Stage B will then
emit no library locks and Stage C will fall back to inference per SHARED §3 and §5.}

================================================================================
PART 4 — TASK
================================================================================

Read the STORY_CONFIG_BLOCK, FULL_STORY, and CHARACTER_LIBRARY above.

Execute Stage B only per every rule and output schema defined earlier in this document.

Preserve English lines exactly.

Make every scene context-aware enough for Stage C image generation.

Propagate Library lock IDs from CHARACTER_LIBRARY and STORY_CONFIG_BLOCK wherever a locked character appears, is referenced, implied, recalled, shown as photo/silhouette/screen/reflection/memory, or carried through pronoun continuity.

Output ONLY the LOCKED SCENE BREAKDOWN.

Do not output commentary, explanation, summary, image prompts, motion prompts, or anything outside the locked scene breakdown.

================================================================================
END OF STAGE B FILE — ENGLISH STORY DOCTOR VERSION
================================================================================
