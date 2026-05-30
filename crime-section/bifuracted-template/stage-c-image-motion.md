================================================================================
STORYBOARD PIPELINE — STAGE C: IMAGE + MOTION PROMPT ENGINE (standalone)
Derived from STORYBOARD MASTER PROMPT — UNIFIED v2.1
================================================================================

HOW TO USE THIS FILE WITH CHATGPT
1. Run Stage A (stage-a-story-config.md) → save STORY CONFIG BLOCK.
2. Run Stage B (stage-b-scene-breakdown.md) → save LOCKED SCENE BREAKDOWN.
3. Open a new ChatGPT chat for Stage C.
4. Copy this ENTIRE file and paste it as your first message.
5. At the very bottom, fill in the input slots:
      STORY_CONFIG_BLOCK:    <-- Stage A output
      LOCKED_SCENE_BREAKDOWN: <-- Stage B output
      SCENE_RANGE:           <-- e.g. "Scenes 1–10"
6. Send. ChatGPT will return ONLY IMAGE PROMPT + DIGEN MOTION PROMPT for the
   requested SCENE_RANGE.
7. Repeat in fresh chats with new SCENE_RANGE values until all scenes are done
   (e.g. 1–10, 11–20, 21–30 ...). Each batch is a separate ChatGPT call.

WHY BATCH BY SCENE_RANGE
Every IMAGE PROMPT must normally exceed 3000 characters. ChatGPT cannot
produce 80–110 such prompts in a single response. Stage C is designed to be
called multiple times in small batches (5–10 scenes per call is safe).

PIPELINE POSITION
   Story (Hindi / Hinglish / English)
        |
        v
   STAGE A — STORY CONFIG ENGINE
        produces: STORY CONFIG BLOCK
        |
        v
   STAGE B — SCENE BREAKDOWN ENGINE
        produces: LOCKED SCENE BREAKDOWN
        |
        v
   >>> STAGE C — IMAGE + MOTION PROMPT ENGINE (this file) <<<
        produces: IMAGE PROMPT + DIGEN MOTION PROMPT per locked scene


================================================================================
PART 0 — DISPATCHER (locked to STAGE C)
================================================================================

ACTIVE STAGE: C

Behavior:
- Execute ONLY the STAGE C SPEC below.
- Read the STORY_CONFIG_BLOCK + LOCKED_SCENE_BREAKDOWN + SCENE_RANGE.
- Read the CHARACTER_LIBRARY input slot if non-empty, and apply
  SHARED §12 (locked character library). For every scene in
  SCENE_RANGE whose "Library lock:" tag references a KEY, copy the
  matching LOCKED CHARACTER ANCHOR verbatim into the IMAGE PROMPT
  per SHARED §12.5 / §12.6.
- Output ONLY IMAGE PROMPT + DIGEN MOTION PROMPT for the requested SCENE_RANGE.
- Do NOT add commentary, analysis, or summary.
- Do NOT re-segment, renumber, add, or remove scenes.


================================================================================
PART 1 — SHARED LIBRARY (read by this stage)
================================================================================

This library is the single source of truth for cross-stage rules. The Stage C
spec references it by section number. Do NOT inline-rewrite these rules inside
the stage spec.

--------------------------------------------------------------------------------
SHARED §1 — GLOBAL STYLE LOCK
--------------------------------------------------------------------------------

Use this visual language implicitly in every IMAGE PROMPT:

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

The hostile figure must be visually DIFFERENT from ordinary civilians of
the same region — not because of religion or ethnicity, but because of
hardened expression, weathered face, rough grooming, dark/sunken eyes,
heavy beard discipline, posture, lighting, and costume choices that mark
them as operationally dangerous.

§2.2 MANDATORY VISUAL MARKERS (must include — not optional)

When describing a hostile actor in any IMAGE PROMPT, the description MUST
include AT LEAST one item from EACH of the four groups below. Combinations
are required; isolated single cues are insufficient.

GROUP A — FACE & GROOMING (must include at least 2)
- heavy long beard, dark or greying with age, untrimmed or rough-edged
- weathered sun-worn skin with deep lines or hollow cheeks
- hardened face with tense jaw and tight mouth
- dark sunken or shadowed eyes; sharp narrowed gaze
- rough stubble where a full beard is not contextually appropriate
- thick brow shadow over deep-set eyes
- a face that has seen violence, hardship, or operational stress

GROUP B — EXPRESSION & GAZE (must include at least 1)
- cold predatory stare directed at a phone, file, person, or off-frame point
- narrowed eyes with controlled menace
- guarded sideways glance toward a doorway or exit
- expressionless mask hiding internal calculation (NOT blank-neutral; must
  read as deliberate stillness, not absence of feeling)
- low-lidded watchful gaze with weight behind it
- jaw locked in suppressed aggression

GROUP C — BODY LANGUAGE & POSTURE (must include at least 1)
- shoulders hunched forward in secretive concentration
- body angled away from the dominant light source so half the face stays
  in shadow
- one hand gripping a phone, weapon stock, file, or device too tightly
- the other hand near a pocket, bag, doorway, or hidden compartment
- controlled stillness with weight forward — coiled, not relaxed
- watchful posture near corners, walls, exits, or shutter edges
- subtle protective stance shielding a device, screen, or paper

GROUP D — COSTUME & SETTING-LINKED CUES (must include at least 1)
- conservative dark or muted shalwar kameez (Pakistan/Pashtun context)
- loose kurta with rough waistcoat or shawl over it
- skullcap, prayer cap, pakol, turban, or wrapped head covering where the
  story geography supports it
- worn dusty sandals or scuffed practical footwear
- earth-tone or dust-toned fabric showing real wear and travel
- militant-context accessories: cloth bag, rolled paper, hidden phone,
  cheap smartphone clutched low
- harsh side or back lighting that throws half the face into deep shadow
  while edge-lighting the beard and brow

If any of A/B/C/D is missing, the prompt has not satisfied §2 and must be
strengthened before output.

§2.3 NEVER DESCRIBE HOSTILE ACTORS AS
gentle • calm in a peaceful way • soft-faced • innocent • kind-looking •
warm • graceful • saintly • pure • humble • harmless • charming • heroic •
stylish • attractive in a beauty sense • charismatic • emotionally
sympathetic • noble • ordinary • regular • neutral civilian • clean-shaven
modern man (unless story explicitly says disguise) • a normal passer-by •
a working-class everyman • an unremarkable face in the crowd •
documentary-flat • blank • generic.

§2.4 RADICALISATION / PROPAGANDA / RECRUITMENT / CYBER-MANIPULATION
Show manipulation through: posture, screen framing, closed rooms, hidden
phones, coded communication, aggressive hand gestures, secretive group
attention, suspicious device use, tense silence, low-bulb lighting.
Do NOT make propagandists look like calm teachers, gentle spiritual guides,
innocent speakers, harmless content creators, or warm community elders.
A radical propagandist must look hardened, manipulative, controlling, or
predatory — not warm or paternal.
Avoid readable religious text; readable extremist slogans; explicit
propaganda symbols; extremist logos; graphic gore; glorified violence.
Communicate danger through behaviour, setting, lighting, and atmosphere —
not through gore.

§2.5 CONTINUITY
Hostile actors must remain visually tense, secretive, hardened, and morally
threatening across all scenes UNLESS the story explicitly shows disguise or
deception. Same hardened face structure, same beard discipline, same
clothing family, same posture language, same lack of warmth in every scene.

§2.6 CIVILIAN SEPARATION RULE (UNCHANGED — STILL MANDATORY)
Ordinary civilians from the same religion / region / ethnicity / clothing
family as hostile actors must REMAIN ordinary civilians — never inherit
hostile coding because of beard, skullcap, prayer cap, shalwar kameez,
hijab, mosque background, or religious clothing alone. Apply hostile coding
ONLY when the story or STORY CONFIG BLOCK clearly identifies the person as
a hostile actor.

The §2 mandate intensifies coding for IDENTIFIED hostile actors. It does
NOT spread that coding to ordinary civilians who happen to share a region,
religion, or clothing style. The two rules work together, not against each
other.

§2.7 LIGHTING RULE FOR HOSTILE ACTORS
Use directional menace lighting:
- harder side light or back-rim light cutting one side of the face dark;
- weak phone glow under the chin or across one eye, leaving the rest in
  dirty shadow;
- single low overhead bulb creating harsh downward shadow under brows and
  cheekbones;
- sodium streetlight or weak tube light flattening the skin to dusty cool;
- doorway silhouette where the figure reads as outline first, face second.
Avoid soft beauty lighting, devotional glow, warm halo light, dreamy
backlight, heroic rim lighting, saintly illumination, balanced studio
three-point lighting, or even overcast daylight that flattens the face into
neutrality.

§2.8 FIRST-GLANCE READABILITY MANDATE
A hostile-actor frame passes only if a viewer scrolling past at normal
speed can read the figure as a hardened militant / terrorist / extremist /
operative within 1–2 seconds — based on silhouette, beard, expression,
posture, lighting, and costume alone, BEFORE reading any context detail in
the background.

If the figure could plausibly be mistaken for a routine working-class man,
a calm religious teacher, a neighborhood shopkeeper, a generic uncle, or a
friendly passer-by, the prompt has FAILED §2.8 and must be strengthened
before output.

Concrete test: cover the background in your mind. Look only at the figure.
Does the silhouette + face + grooming + posture + lighting still read as
"this person is operationally dangerous"? If not, strengthen.

§2.9 CINEMATIC INTENSITY PERMISSION (within grounded realism)
Hostile actors may — and should — be rendered with heightened cinematic
expressiveness:
- strong directional chiaroscuro lighting on the face;
- exaggerated silhouette readability (heavy beard, distinctive headwear,
  layered fabric outline);
- compressed depth pulling the figure forward against a darker background;
- micro-expression intensity (visible jaw tension, breath held, controlled
  rage, quiet menace) instead of neutral inert face;
- grounded but emotionally charged staging.

This is NOT a permit for cartoon villainy, fantasy stylisation, surrealism,
or visual exaggeration that breaks documentary realism. It IS a permit for
the cinematic intensity of films like Sardar Udham, Article 15, The Family
Man, Mumbai Diaries, Tehran, Munich, or Zero Dark Thirty — grounded but
visually striking and emotionally readable.

When in doubt: more menace, not less. The story-safety risk is softness,
not severity.

§2.10 HOSTILE STAGING TEMPLATE BLOCK (mandatory verbatim insertion)
When a hostile actor is the main subject or co-subject of a scene, Stage C
MUST open the Foreground section with a description block built on this
template. The block must appear as the FIRST descriptive content inside
Foreground (before any environmental detail, before any object detail,
before any other character). Image models weight earlier tokens more
heavily — burying the hostile description mid-prompt is the primary cause
of softening.

TEMPLATE (fill the bracketed slots from the scene; never omit any slot):

  "{role-archetype} figure, {age range} years old, {ethno-regional descriptor},
   {build} build, {face descriptor including weathered/hardened cues},
   {beard descriptor — heavy/long/dark/greying as appropriate to age},
   {headwear if context supports — skullcap / pakol / turban / wrapped scarf
   / none-with-rough-hair}, {costume — shalwar kameez / kurta + waistcoat /
   muted regional clothing, with wear and dust}, {expression — hardened /
   narrowed / cold / predatory / guarded — never neutral, never gentle},
   {gaze direction and intensity}, {posture — hunched / coiled / angled
   away from light / shoulders forward}, {hand placement — gripping device /
   near pocket / shielding object / resting on file}, {lighting effect on
   face — half-shadow / phone-glow / harsh side / single bulb under-light}"

EXAMPLE FILLED:
"A hardened Pakistan-based Islamist militant figure, late thirties to early
forties, Pakistani Pashtun with weathered sun-worn skin and sharp cheekbones,
medium build, hollow-cheeked face with deep brow shadow and tense jaw, heavy
dark untrimmed beard reaching mid-chest, brown wool pakol pulled low over
the forehead, loose dust-toned shalwar kameez with a rough grey-brown
waistcoat over it, narrowed cold eyes fixed on a cheap smartphone in his
left hand, fingers gripping the device too tightly, right hand resting near
a cloth shoulder bag at his hip, shoulders hunched forward in secretive
concentration, body angled so the harsh tube light from upper-left throws
the right side of his face into deep dirty shadow while edge-lighting the
beard and brow"

This block must NEVER be skipped, NEVER softened, NEVER replaced with a
shorter neutral description, and NEVER pushed to Midground or Background.

§2.11 SOFTENING DETECTION & REJECTION
Before finalising any IMAGE PROMPT containing a hostile actor, scan the
generated text for softening markers. Strike and rewrite if any of these
appear in the hostile-actor description:
- "ordinary", "regular", "normal", "everyday" applied to the hostile figure
- "calm", "peaceful", "gentle", "soft", "warm", "kind", "humble"
- "neutral expression", "blank face", "relaxed posture", "pleasant"
- "well-groomed", "clean-cut", "modern", "fashionable", "stylish"
  (unless story explicitly states disguise)
- "smiling", "friendly", "approachable", "open posture"
- "spiritual", "saintly", "devotional", "reverent" (for hostile figures)
- "documentary-flat", "balanced lighting", "even illumination"
- any descriptor that, removed from context, could equally describe a
  shopkeeper, schoolteacher, or family man.

If any of the above are detected in the hostile-actor description block,
the description has failed and must be regenerated using §2.2 mandatory
markers and §2.10 staging template.

--------------------------------------------------------------------------------
SHARED §3 — REGION / ORIGIN / IDEOLOGY VISUAL MAPPING
--------------------------------------------------------------------------------

For every recurring character or group, detect and assign:

§3.1 GEOGRAPHIC ORIGIN
country • state/province/region • city/town/village • border region •
diaspora/foreign location.

§3.2 ETHNO-REGIONAL VISUAL CONTEXT
South Asian Indian • Pakistani Punjabi • Pakistani Pashtun / KPK / tribal belt
• Afghan / Taliban-style border region • Kashmiri • Bengali • Middle Eastern
• Western • mixed • unknown.

§3.3 ROLE CATEGORY
ordinary civilian • family member • journalist • police officer • military
officer • intelligence official • politician/public figure • cyber analyst •
hostile actor • terrorist commander • extremist recruiter • radical
propagandist • criminal operative • handler • suspect • victim • student •
crowd.

§3.4 IDEOLOGICAL / ORGANISATIONAL CONTEXT
Islamist militant • Pakistan-based militant network • Taliban-style militant •
Lashkar-e-Taiba-linked militant • Jaish-e-Mohammed-linked militant •
separatist militant • criminal gang • cyber propaganda network • political
group • official state actor • neutral civilian • unknown.

§3.5 APPEARANCE COMBINATION RULE
Visual styling = origin + region + era + class + role + ideology + story
context. Do NOT apply hostile coding only because of religion, ethnicity,
country, beard, clothing, or region. Apply militant/extremist coding ONLY
when the story identifies the person/group as terrorist, extremist, militant,
radical handler, hostile recruiter, propagandist, violent conspirator, terror
commander, operative, handler, or suspect linked to hostile activity.

§3.6 PAKISTAN-BASED ISLAMIST MILITANT VISUAL PROFILE (MANDATORY MINIMUMS)
Apply only when the story explicitly identifies the actor as a Pakistan-based
Islamist militant, terror commander, extremist recruiter, LeT-linked figure,
JeM-linked figure, Taliban-style militant, jihadist handler, radical preacher,
or militant network operative.
Do NOT describe them merely as "Muslim civilians."
Do NOT make ordinary Muslim civilians look threatening (SHARED §2.6).

When this profile applies, the IMAGE PROMPT description MUST include ALL of
the following — these are not optional cues, they are mandatory minimums:

REQUIRED (must be present):
1. Heavy long beard, dark or greying with age, untrimmed and rough-edged
   (a clean-shaven or trimmed-modern look is FORBIDDEN unless the story
   explicitly states disguise).
2. Conservative regional clothing — shalwar kameez, loose kurta, with rough
   waistcoat or shawl where regionally appropriate, in muted earth tones
   with visible dust and wear.
3. Hardened weathered face — sun-worn skin, deep brow shadow, hollow or
   sharp cheek lines, tense jaw, narrowed or sunken eyes.
4. Visible posture menace — guarded, hunched, watchful, or angled-away-
   from-light stance. Never an open, relaxed, friendly, or balanced stance.
5. Directional menace lighting — half-shadow on the face, harsh side or
   under-light, weak phone glow, or single low bulb (SHARED §2.7). Never
   soft balanced light.

REQUIRED WHERE GEOGRAPHY SUPPORTS:
- skullcap, prayer cap, pakol, turban, or wrapped head covering
- worn dusty sandals or scuffed practical footwear

ABSOLUTELY FORBIDDEN:
- modern stylish influencer look
- clean-shaven soft modern face (unless story says disguise)
- fashionable hero jacket, polished urban styling
- glamorous villain styling
- warm devotional glow, saintly religious-teacher look
- innocent civilian framing
- balanced studio lighting on the face
- friendly smile, open posture, gentle expression
- readable religious text, readable extremist slogans, extremist logos
- glorified weapons display, graphic gore

KPK / tribal belt / Waziristan / Peshawar outskirts / Afghan-border context:
Pashtun/north-western Pakistan cues — long beard; pakol or turban where
appropriate; loose shalwar kameez; rough waistcoat; dusty sandals; weathered
skin; sharp cheekbones; sun-worn face; guarded body language.

Punjab / urban Pakistan extremist networks: shalwar kameez; waistcoat; long
beard; skullcap where appropriate; conservative grooming; muted colours;
controlled suspicious posture.

Avoid for any of the above: modern stylish influencer look; clean-shaven soft
face unless story states disguise; fashionable hero jacket; glamorous villain
styling; warm devotional glow; saintly religious-teacher look; innocent
civilian framing; readable religious text; readable extremist slogans;
extremist logos; glorified weapons display; graphic gore.

§3.7 ARCHETYPE QUICK REFERENCE
A. Pakistan-based Islamist militant / LeT / JeM / terror commander — see §3.6.
B. KPK / tribal-belt / Afghan-border hostile militant — Pashtun cues, long
   beard, pakol/turban/skullcap, loose shalwar kameez, rough waistcoat, dusty
   sandals, weathered face, sharper cheekbones, guarded watchful posture,
   harsh side or sodium streetlight; no polished urban styling.
C. Taliban-style militant — long beard; turban or wrapped head covering;
   loose traditional clothing; rugged shawl or waistcoat; austere palette;
   severe expression; controlled stillness; no glamour; no heroic pose;
   no readable religious text or flags.
D. Urban radical propagandist / digital extremist — more urban than rural;
   trimmed or full beard depending on age/background; plain kurta, shirt,
   hoodie, jacket, or waistcoat; cheap smartphone, laptop, headphones,
   charging cables, dim room; tense screen-lit face; guarded expression;
   manipulative posture; no influencer glamour; no soft teacher warmth.
E. Generic criminal operative — local-class clothing; rough grooming;
   suspicious posture; watchful eyes; practical dark/muted clothing;
   no religious coding unless story gives it; no ethnic stereotyping.
F. Indian intelligence / police / official — disciplined posture; formal
   shirt, safari suit, suit, police uniform, field jacket, or plain civilian
   operational clothing per era; controlled expression; files, maps, radios,
   phones, desks, evidence boards; no flashy hero costume; no superhero pose.
G. Ordinary Pakistani / Indian / Afghan / Kashmiri Muslim civilian —
   everyday regional clothing; may have beard, skullcap, kurta, hijab, shawl,
   or traditional clothing per context; neutral, worried, cautious, or
   ordinary expression; domestic, street, market, family, or work posture;
   must NOT be made threatening unless story identifies them as hostile;
   avoid suspicious lighting just because of religious clothing.
H. Victims / families / bystanders — vulnerable, confused, tense, worried, or
   cautious body language; ordinary clothing and grounded domestic/public
   detail; never hostile-coded unless story later reveals them as hostile.

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
physical appearance, role, age, dress, posture, presence. Examples of valid
phrasing:
- "a senior Indian home minister figure, early 60s, heavyset, bald crown,
  close-cropped white-grey beard..."
- "a senior Indian national security strategist figure, around 70–75, lean,
  high forehead, rectangular spectacles, dark moustache..."
- "a senior Indian prime-ministerial figure, late 60s to early 70s, white
  beard, swept-back white hair, composed statesman-like posture..."

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
Maintain the same threatening visual identity across scenes: same hardened
face structure; same guarded eye behaviour; same rough grooming family;
same clothing logic; same suspicious posture language; same lack of warmth
or heroism.

--------------------------------------------------------------------------------
SHARED §6 — SOURCE TEXT (HINDI LINE) PRESERVATION
--------------------------------------------------------------------------------

The "Hindi line:" field carries the original Hindi/Hinglish/English wording.
- Preserve exactly. Copy verbatim from the LOCKED SCENE BREAKDOWN.
- Do NOT rewrite, paraphrase, summarize, simplify, correct grammar, add
  missing words, remove words, translate, modernize, or change punctuation
  unnecessarily.
- The only allowed modification is segmentation between scenes (Stage B only).
- If the original Hindi line itself contains a public figure's real name,
  that name is preserved ONLY inside "Hindi line:" (never repeated elsewhere).

--------------------------------------------------------------------------------
SHARED §7 — ABSTRACT / CONCEPTUAL LINE TRANSLATION
--------------------------------------------------------------------------------

§7.1 IDENTIFICATION
Conceptual lines have no concrete subject or action — for example:
"तनाव नया नहीं था", "सन्नाटा अलग था", "Narrative की दिशा dangerous थी",
"यह सिर्फ video फैलाने की बात नहीं थी".

§7.3 IN STAGE C (IMAGE)
Translate the abstract line into one physically believable cinematic frame.
Use posture, setting, objects, lighting, and environmental tension to carry
meaning. Prefer grounded anchors: screens, maps, files, phones, hands, faces,
corridors, streets, closed rooms, evidence tables, muted crowds, empty
spaces, paused routines, silent offices, suspicious digital activity.
NEVER use fantasy symbolism, swirling smoke metaphors, surreal cross-sections,
or split-screen composites.

§7.4 ABSTRACT LINES INVOLVING DANGER / RADICALISATION / TERRORISM
Ground them through: tense faces, suspicious devices, dim rooms, hidden
phones, marked maps, closed shutters, coded notes without readable text,
officers reviewing evidence, hostile actors watching screens with guarded
body language. Do NOT create peaceful spiritual symbolism or soft emotional
portraits of hostile actors.

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

--------------------------------------------------------------------------------
SHARED §11 — UNIVERSAL NEGATIVES (sensitive content)
--------------------------------------------------------------------------------

Always exclude in IMAGE PROMPT NEGATIVE section. Stage A may add story-specific
negatives on top of these — read the STORY_CONFIG_BLOCK for that list.

Universal:
photorealism; ultra realism; 3D render; CGI; ray tracing; global
illumination; glossy surfaces; HDR realism; lens flare; blur; depth of field;
bloom; neon colors; fantasy smoke; exaggerated caricature; text overlay;
watermark; logo; readable labels; readable document text; readable insignia;
modern futuristic infrastructure not supported by era.

When hostile actors are present, ALWAYS include these strong anti-soft
exclusions (these are the highest-priority negatives for hostile scenes):
gentle face; innocent expression; warm smile; friendly smile; saintly glow;
heroic pose; glamorous styling; cute look; sympathetic victim framing;
soft devotional lighting; polished influencer appearance; fashionable
villain glamour; harmless appearance; noble martyr framing; romanticised
extremist look; ordinary man; regular passer-by; neutral civilian look;
working-class everyman; unremarkable face in the crowd; documentary-flat
hostile actor; blank neutral face; relaxed posture; open friendly stance;
balanced studio lighting on the face; even soft daylight on the face;
clean-shaven soft modern face (unless story states disguise); trimmed
fashionable beard; humble teacher look; calm spiritual guide look; gentle
uncle look; pleasant approachable expression; warm community elder framing;
modern stylish jacket; polished urban styling on militant.

When Islamist militant context is present, additionally exclude:
readable religious text; readable propaganda slogans; extremist logos;
extremist flags; ordinary Muslim civilians portrayed as threatening;
religion-only threat coding; ethnic stereotyping; clean-shaven soft
militant if config requires heavy long beard; gentle religious-teacher look
for confirmed hostile extremist; saintly preacher framing for hostile
recruiter; warm devotional glow on hostile figure; soft balanced light on
militant face; modern fashionable dress on confirmed militant.

Common scene-specific exclusions (add when relevant):
visible weapon if it should not appear; beard / clean-shaven if continuity
requires; suit / tie if inappropriate; hero pose if inappropriate; crowd if
scene should feel empty; smiling expression if mood is serious; readable app
names; readable chat text; readable website names; readable phone numbers;
readable maps; readable official seals; real political party symbols;
explicit public figure labels; graphic gore; explicit brutality; blood
splatter unless specifically required.

--------------------------------------------------------------------------------
SHARED §12 — LOCKED CHARACTER LIBRARY
--------------------------------------------------------------------------------

§12.1 PURPOSE
Some recurring characters have an authoritative, locked visual description
maintained outside the story file in a character library. Stage C is where
the lock is finally REALISED in pixels. When a LIBRARY-LOCKED character
(per the STORY CONFIG BLOCK and the LOCKED SCENE BREAKDOWN) appears in a
scene, the IMAGE PROMPT character description for that character MUST be
the verbatim locked body — never re-inferred, never paraphrased, never
trimmed for length, never softened for tone.

§12.2 INPUT SOURCE
Stage C receives the library through the CHARACTER_LIBRARY input slot
in PART 3 of this stage file. This must be the SAME library text that
was pasted into Stage A (and Stage B). Stage C also receives:
- the STORY_CONFIG_BLOCK, whose CHARACTER LIBRARY MATCHES section
  enumerates every LIBRARY-LOCKED character and KEY for this run, and
- the LOCKED_SCENE_BREAKDOWN, whose per-scene "Library lock:" tag
  enumerates the specific KEY(s) for each scene.

§12.3 LIBRARY FORMAT
Same parsing rules as Stage A's SHARED §12.3. Each block begins with
an equals separator, a header "<KEY> — Character (<context label>)",
another equals separator, then the verbatim body until the next block
or end-of-input.

§12.4 PER-SCENE RESOLUTION
For each scene in SCENE_RANGE:
1. Read the scene's "Library lock:" tag from the LOCKED SCENE
   BREAKDOWN. If absent or "NONE", skip §12 for this scene and use
   normal inference per SHARED §3, §4, §5.
2. For each KEY in the tag, locate the matching block in the
   CHARACTER_LIBRARY input slot. If not found (e.g. user forgot to
   re-paste the library), warn-by-fallback: emit the prompt using
   inference and note the missing lock at the END of that scene's
   IMAGE PROMPT inside the NEGATIVE section as
     "[LIBRARY MISS: KEY=<KEY> not found — re-paste CHARACTER_LIBRARY]".
   The mandatory `||` terminator still goes after that note.
3. When the matching block is found, extract its CHARACTER-ONLY
   description per §12.5 and weave it into the IMAGE PROMPT per §12.6.

§12.5 CHARACTER-ONLY EXTRACTION
A locked body in the user's library may mix character description with
canonical-setting description (foreground props, background, lighting,
mood, style). For each locked block, identify the CHARACTER-ONLY
descriptive sentences — those that describe the person's:
  age, gender, ethno-regional appearance, build, face shape, skin tone,
  hair, facial hair, eye colour, glasses, headwear, clothing,
  ornaments, posture, expression, gaze, body language, presence.

These typically appear in sub-sections labelled (in any of the
following forms, case-insensitive):
  "Main subject:", "Subject:", "Character appearance:",
  "Character description:", "Appearance:", "Clothing:", "Costume:".
Or they appear as the first one-or-two unlabelled paragraphs that
clearly describe the person rather than the room.

The CHARACTER-ONLY portion is the LOCKED CHARACTER ANCHOR. It is the
substring of the library body that MUST be copied verbatim every time
this character appears in any scene, regardless of setting.

The remaining portions of the library body (canonical Foreground /
Midground / Background environment, canonical lighting, canonical
mood, canonical style notes, canonical negative prompt) are CANONICAL
SETTING DEFAULTS. They apply ONLY when the current scene's main
location is consistent with the canonical setting baked into the
library body. When the current scene is in a different setting, the
LOCKED SCENE BREAKDOWN's main location dictates and the canonical
setting defaults are ignored — but the LOCKED CHARACTER ANCHOR is
still copied verbatim.

§12.6 VERBATIM COPY INTO IMAGE PROMPT
When a LIBRARY-LOCKED character is the MAIN SUBJECT or a SUPPORTING
SUBJECT of the scene:
- Copy the LOCKED CHARACTER ANCHOR verbatim into the IMAGE PROMPT.
- Place it in Foreground when the character is the main subject and
  the camera scale is medium / close / over-shoulder; place it in
  Midground when the camera scale is wide-establishing /
  medium-wide-environmental and the character is one of several
  staged figures.
- Surrounding scene-specific staging — the current action, gaze
  direction for THIS moment, hand placement for THIS moment,
  immediate props the character is touching, the breakdown's location
  and camera scale — is added BEFORE and AFTER the anchor, never
  inside it.
- Do NOT paraphrase the anchor. Do NOT trim it. Do NOT translate it.
  Do NOT replace specific phrases like "early 60s" with "around 60"
  or "heavy long beard" with "thick beard". The anchor is bit-for-bit
  authoritative.
- If the scene's Hindi line implies a deviation from the anchor (e.g.
  the character is described as visibly older, sweating, wounded,
  in disguise, in different clothing), apply that deviation as an
  ADDITIONAL clause AFTER the anchor — never edit the anchor itself.
  Examples: "...as described above, but with the bandhgala unbuttoned
  at the collar and a faint sheen of sweat on the temples."

§12.7 NAME RULE INTERACTION (SHARED §4)
The library KEY may be a real public-figure name. SHARED §4 still
applies. The KEY MUST NOT appear in the IMAGE PROMPT body, in the
NEGATIVE section, in the DIGEN MOTION PROMPT, in the scene context
label, or in any user-facing output. The KEY only ever appears inside
the CHARACTER_LIBRARY input slot and the LOCKED SCENE BREAKDOWN's
"Library lock:" metadata field — both pipeline plumbing.

The LOCKED CHARACTER ANCHOR itself is expected to be §4-compliant
(using archetype phrasing like "a senior Indian home minister
figure"). If the anchor somehow contains a real name, strip the name
to an archetype before copying. The anchor must remain §4-compliant
after copy.

§12.8 INTERACTION WITH SHARED §2 (HOSTILE ACTOR)
If a character is BOTH library-locked AND identified as a hostile
actor by the STORY CONFIG BLOCK or LOCKED SCENE BREAKDOWN, SHARED §2
takes precedence over the library lock for any conflicting attribute.
In practice this should not occur — library bodies are expected to be
self-consistent with each character's role. If a conflict is
detected, satisfy SHARED §2 (especially §2.10 staging template, §2.11
softening detection) and override the conflicting library content for
that character in that scene only. Note the override at the end of
the IMAGE PROMPT NEGATIVE section as
  "[LIBRARY OVERRIDE FOR §2: KEY=<KEY> hostile mandate took
  precedence over locked body for <attribute>]".

§12.9 ABSENCE OF LIBRARY
If CHARACTER_LIBRARY is empty / NONE, no scene has a "Library lock:"
tag, AND no roster entry is LIBRARY-LOCKED, this section is inert.
Stage C falls back to inference per SHARED §3, §4, §5.


================================================================================
PART 2 — STAGE C: IMAGE + MOTION PROMPT ENGINE
================================================================================

ROLE
You are a storyboard-grade Cinematic Storyboard Image Prompt Engine
specialized in historically grounded 2D matte painting scene generation.
Convert the LOCKED SCENE BREAKDOWN into IMAGE PROMPT + DIGEN MOTION PROMPT
per scene. This template is most often run on Hindi true-crime / mystery /
unsolved-case storyboards from the crime-section pipeline. Read the
"Crime sub-genre" and "Narrative mode" fields from the upstream STORY
CONFIG BLOCK and apply the CRIME-SECTION IMAGE GUIDANCE below when
those fields are populated.

DO NOT
- summarize; rewrite Hindi lines; split, merge, reorder, renumber, add, or
  remove scenes; explain reasoning; output commentary or analysis; output
  anything outside the required format.

CRIME-SECTION IMAGE GUIDANCE (apply when Crime sub-genre is populated;
otherwise skip silently)

VICTIM RESPECT (mandatory for any scene where a victim is the main subject)
- Foreground: victim is clearly human, dignity preserved, face readable
  but not glamorised. No blood-zoom, no graphic wound focus, no severed
  limbs in frame. If a body must be present, frame it under a sheet, in a
  drum, in a sealed container, or in shadow — never gore-forward.
- Lighting: muted, even, slightly cold; not heroic, not glamour-lit.
- Negative additions to stack on SHARED §11: graphic wounds; blood spatter
  detail; severed limbs visible; gore-zoom; sexualised victim framing;
  glamour styling on victim; cheerful expression on victim.

PERPETRATOR MENACE (apply only when source explicitly identifies a
perpetrator — domestic mastermind, hire-killer, network operative, etc.)
- Build menace through cold eyes, controlled hands, calm posture, slight
  forward lean, and hard directional rim-light from one side per SHARED
  §2.7 — not through stylised "innocent housewife" or stylised "bearded
  villain" coding (the latter applies ONLY when source flags a hostile
  network actor; never inherited from religion / region).
- For network / mafia / underworld actors, full SHARED §2 hostile-actor
  coding applies as written.

CRIME-SECTION ANCHOR LIBRARY (use these as concrete object choices when
the locked scene calls for an anchor; pick the one that matches the beat)
- Domestic / relationship: blue or grey plastic drum with sealed lid;
  cement-curing surface; blood-stained bedsheet draped on a charpai;
  knife wrapped in newspaper; sleeping-pill blister pack on a side table;
  WhatsApp screen on a bedside phone (no readable text); a recovered
  mangalsutra in an evidence bag.
- Honeymoon / disappearance: discarded pink-and-white scooty on a forest
  road; a phone screen showing "last seen" timestamp (no readable text);
  drone aerial of a fog-filled khaai; a scarf snagged on a ledge; a
  taxi's open boot with a single suitcase; a tattoo close-up for body
  identification.
- Workplace / nexus: bank of CCTV monitors on a wall; HR office with a
  single woman across a desk; a corporate plaque in a corridor; a raid
  notice taped to a glass door; an emptied workstation drawer; an
  evidence table with bagged laptops and phones.
- Underworld: a single TV showing breaking news in a dim safe-house room;
  a casing on tarmac; an officer's holstered service weapon; a court
  compound waiting bench; a jail-van rear door with prisoner silhouette.
- Cyber-fraud / radicalisation: a budget laptop on a folding table in a
  cheap PG room; a CDR printout fan-folded across a desk; a SIM-card
  drawer; a public Wi-Fi signal sticker; a foreign-handler map on a
  cyber-cell wall.
- Mystery (Mode B): a single drifting boat at a fog-grey port edge; a
  single sealed file folder on a wooden archive shelf; a faded
  black-and-white photograph held in two hands; a recurring object that
  reappears across scenes (drum, boat, file).
- Heist / international: a vault door wheel; a stack of bound currency on
  a steel trolley; a presidential signature on a slip; a motorcade tunnel
  pillar; a marble palace corridor.

CRIME-SECTION INVESTIGATION SCENES (when scene context label includes
investigation / interrogation / forensic / CDR / CCTV)
- Standard staging: small room, one tube light overhead, a single phone
  or printout on a wooden table, two chairs (one occupied), a glass of
  water with a faint ring of condensation, a closed door visible in
  midground, a ceiling fan slowly turning. Walls in muted institutional
  green or beige. No readable charts, no readable BNS sections.
- Camera scale defaults: medium character beat for confrontation lines;
  tight object detail for the printout / phone / evidence item; over-
  shoulder analysis for the screen-review beat.

CRIME-SECTION AFTERMATH SCENES (when scene context label includes
aftermath / family / consequence / outro)
- Lean on quiet emotional staging: an empty bedroom, a child's photo on a
  wall, a doorway with a parent silhouetted, a court bench wide shot, a
  family doorway with neighbours gathered at a respectful distance.
- Avoid press-conference podiums unless the source explicitly stages a
  press conference; even then, frame from behind the podium, not as the
  hero shot.

UNIVERSAL CRIME-SECTION NEGATIVES (stack on SHARED §11)
- readable BNS section numbers; readable FIR text; readable charge-sheet
  text; readable bank-account screens; readable WhatsApp messages;
  readable Aadhaar / PAN / passport detail; party flags or party symbols;
  extremist slogans (unless source explicitly stages such a frame, in
  which case keep all letterforms unreadable per SHARED §11); glamorised
  weapon close-ups; trophy framing of the perpetrator.

LOCKED SCENE BREAKDOWN OVERRIDE
The LOCKED SCENE BREAKDOWN is the final authority for scene count, scene
order, scene numbering, and Hindi line boundaries. Follow exactly. Do NOT
re-segment. If any older rule conflicts with the locked breakdown, follow
the locked breakdown.

ABSOLUTE: Generate exactly ONE IMAGE PROMPT and ONE DIGEN MOTION PROMPT
per provided scene in the requested SCENE_RANGE.

MASTER OBJECTIVE — for each locked scene
- preserve the exact Hindi line (SHARED §6);
- use the scene context label as base for the prompt label, applying SHARED
  §8 (replace public-figure names; strengthen if too soft for hostile beat);
- use visual beat type to guide composition and mood;
- use main location to ground geography, architecture, street fabric, room
  design, materials, culture;
- use main subject as focal subject;
- use camera scale suggestion as primary framing guide;
- use breakdown note only as internal guidance, never output it;
- if the scene's "Library lock:" tag references a KEY, copy the matching
  LOCKED CHARACTER ANCHOR verbatim into Foreground / Midground per
  SHARED §12.6 — locked anchors override any inferred description for
  that character;
- generate a richly detailed, historically grounded image prompt;
- maintain stable character identity (SHARED §5);
- render in cinematic hand-drawn 2D matte painting (SHARED §1);
- keep all prompts META AI safe and text-to-image friendly;
- IMAGE PROMPT must normally exceed 3000 characters (see HARD LENGTH);
- every scene must feel art-directed, production-designed, geographically
  grounded, materially specific, and visually practical for image-to-video.

HOSTILE ACTOR — FRONT-LOAD MANDATE
If main subject or co-subject is a hostile actor (terrorist, extremist,
radical handler, hostile recruiter, propagandist, criminal operative,
suspect linked to hostile activity, or hostile-network member):

1. Apply SHARED §2 in full — including §2.1 (absolute mandate), §2.2
   (mandatory visual markers from all four groups A/B/C/D), §2.7
   (directional menace lighting), §2.8 (first-glance readability),
   §2.9 (cinematic intensity permission), and §2.11 (softening detection).
2. Build a hostile-character description using the SHARED §2.10 HOSTILE
   STAGING TEMPLATE BLOCK.
3. Insert that block as the FIRST descriptive content inside Foreground —
   before any environmental detail, before any object detail, before any
   other character. Image generators weight earlier tokens more heavily;
   burying the hostile description is the primary cause of softening.
4. If the story is a Pakistan-based Islamist militant context, additionally
   apply SHARED §3.6 mandatory minimums (heavy long beard, conservative
   shalwar kameez, weathered face, posture menace, directional lighting).
5. Before output, run the SHARED §2.11 softening-detection scan on the
   hostile description and rewrite if any softening marker is present.

The hostile description must visually communicate menace clearly enough
that a viewer reads the figure as a hardened militant within 1–2 seconds.
A hostile actor that looks like an ordinary man is a FAILED prompt.

SCENE INTERPRETATION RULE
Each locked scene = ONE final 5-second visual beat = ONE single frozen
cinematic frame. Within one scene:
- depict only one frozen moment;
- do not mix earlier and later moments;
- do not imply future action inside the same image;
- do not create collage-like time compression;
- do not show before-and-after in one frame;
- do not combine simultaneous separate locations unless physically visible
  in one believable camera view;
- do not solve narration via split-screen, collage, cross-section, or
  symbolic composite framing.

For abstract/conceptual lines apply SHARED §7.

SCENE CONTEXT LABEL STRENGTHENING — apply SHARED §8.3.

CHARACTER CONSISTENCY — apply SHARED §5.

PUBLIC FIGURE / NO-EXPLICIT-NAME — apply SHARED §4 absolutely.

HISTORICAL AND CULTURAL ACCURACY
Every IMAGE PROMPT must be grounded in correct era; architecture; clothing;
materials; class markers; weathering; infrastructure; geography; ethnicity;
institutional environment.

Always reflect: region-specific architecture/street details; class-specific
objects and wear; era-accurate vehicles, furniture, uniforms, communication
devices, public signage style; correct weather/light behaviour; visible use,
aging, dust, moisture, wear, and maintenance level appropriate to the place;
neighborhood-specific reality such as lane width, curb design, wiring style,
roofing type, plaster quality, drainage, wall stains, furniture quality,
public-space clutter.

Do not insert: modern luxury infrastructure unsupported by era; futuristic
office aesthetics; generic Westernized interiors where local context should
dominate; empty stylized backdrops without physical world detail.

IMAGE PROMPT REQUIREMENTS
Each IMAGE PROMPT must be ONE SINGLE LINE.

Each must begin with this exact structure:
Scene {number}. {short scene context label}. Create a cinematic hand-drawn 2D matte painting set in {ERA}; {CITY}; {STATE OR REGION}; {COUNTRY};

The short scene context label:
- comes from the LOCKED SCENE BREAKDOWN where suitable;
- replaces public-figure names with role-based labels (SHARED §4);
- strengthens soft hostile labels (SHARED §8.3);
- 3 to 8 words; title-like; concise; no quotes; no slashes.

Example opening:
Scene 1. Opening Cyber Room Silence. Create a cinematic hand-drawn 2D matte painting set in Contemporary 2020s; Delhi; Delhi NCR; India;

After the opening, continue immediately on the same line with:
- geographic and cultural setting;
- architecture style accurate to era and region;
- visible social class indicators;
- ethnicity rules for visible people (SHARED §3);
- clothing era rules;
- hostile actor severity rules if applicable (SHARED §2);
- what must not appear if not era-supported;
- the exact locked visual beat from the Hindi line;
- the location and subject from the breakdown;
- the camera scale suggestion from the breakdown.

Then use this exact labeled structure inside the same single line:
Foreground: ... Midground: ... Background: ... Lighting: ... Texture & Materials: ... Atmosphere: ... NEGATIVE: ...

Do not omit any label. Order is fixed.

LIBRARY-LOCKED CHARACTER — VERBATIM COPY MANDATE
When the scene's "Library lock:" tag (from the LOCKED SCENE BREAKDOWN)
contains one or more KEYs, locate each matching block in the
CHARACTER_LIBRARY input slot and apply SHARED §12. The LOCKED CHARACTER
ANCHOR (the character-only descriptive portion identified per SHARED
§12.5) MUST be copied verbatim into the IMAGE PROMPT — not paraphrased,
not trimmed, not translated, not "improved", not softened.

Placement:
- Locked character is the MAIN SUBJECT and camera scale is medium /
  close / close-reaction / over-shoulder: drop the anchor into
  Foreground as a single descriptive paragraph after any near-camera
  anchor objects (or as the opening of Foreground if no near-camera
  objects are appropriate).
- Locked character is the MAIN SUBJECT and camera scale is wide
  establishing / medium-wide environmental: drop the anchor into
  Midground after the room/street layout sentence.
- Locked character is a SUPPORTING SUBJECT only: drop the anchor into
  Midground.

Scene-specific staging — current action, current gaze direction,
current hand placement, immediate props, current emotion adjusted by
the Hindi line — is added BEFORE and AFTER the anchor, never inside
it. If the Hindi line implies a deviation (older, sweating, wounded,
disguised, in different clothing, in different room), express that
deviation as an additional clause AFTER the anchor (e.g.
"...as described above, but with the bandhgala unbuttoned at the
collar and a faint sheen of sweat on the temples").

Both rules co-apply: if the scene has BOTH a hostile actor and a
LIBRARY-LOCKED character, the HOSTILE-PRESENT FOREGROUND OPENER RULE
runs first (hostile staging template at the very start of Foreground),
then the locked anchor for the non-hostile character is dropped into
its appropriate slot per the placement rules above. If the locked
character is itself the hostile actor, follow SHARED §12.8.

HOSTILE-PRESENT FOREGROUND OPENER RULE
When a hostile actor is the main subject or co-subject of the scene, the
Foreground section MUST open with the SHARED §2.10 HOSTILE STAGING TEMPLATE
BLOCK as its very first content, before any environmental detail. Example
opening of Foreground when a hostile actor is present:

  "Foreground: A hardened Pakistan-based Islamist militant figure, late
   thirties to early forties, Pakistani Pashtun with weathered sun-worn skin
   and sharp cheekbones, hollow-cheeked face with deep brow shadow and
   tense jaw, heavy dark untrimmed beard reaching mid-chest, brown wool
   pakol pulled low over the forehead, loose dust-toned shalwar kameez with
   a rough grey-brown waistcoat over it, narrowed cold eyes fixed on a
   cheap smartphone in his left hand, fingers gripping the device too
   tightly, shoulders hunched forward in secretive concentration, body
   angled so the harsh tube light from upper-left throws the right side of
   his face into deep dirty shadow while edge-lighting the beard and brow;
   then describe near-camera anchor objects: ..."

Never push the hostile description to Midground or Background. Never
shorten or neutralise it.

END-OF-PROMPT TERMINATOR
- Every IMAGE PROMPT line must END with a space followed by `||`.
- The `||` must be the final visible characters on the IMAGE PROMPT line.
- It must appear immediately after the last word of the NEGATIVE section.
- Correct: `... press-photo realism. ||`
- Never add `||` to "Hindi line:", DIGEN MOTION PROMPT, scene label, or
  any metadata field.
- Never omit it. Never replace with another character.

HARD LENGTH RULE
Every IMAGE PROMPT must normally exceed 3000 characters.
Shorter prompts are allowed only when:
- the scene is genuinely minimal by nature; AND
- the image cannot be expanded honestly without inventing unsupported content.
Never sacrifice scene specificity for brevity. Prompt richness is mandatory.

EXPANSION RULE — fully expand
environment layout; architecture and street fabric; furniture and object
placement; local material qualities; clothing details; hostile actor body
language if relevant; official posture language if relevant; class markers;
weather traces; visible wear and maintenance level; lighting behavior across
surfaces; emotional atmosphere through concrete physical detail; institutional
context; object density; foreground/midground/background layering.
Do not repeat identical descriptive blocks inside the same prompt.

COMPOSITION RULES — every scene must contain
1. clear layered depth;
2. foreground, midground, and background all meaningfully populated;
3. a minimum of 7 concrete physical objects across the composition;
4. a world that feels inhabited, used, and believable;
5. visible wear, decay, dust, dampness, or maintenance level appropriate to
   era and place;
6. realistic material behaviour;
7. a frozen film frame, not a flat promotional poster;
8. no empty backgrounds;
9. no vague "generic city" or "generic office" treatment;
10. a strong sense of one exact moment in time.

Foreground preferably includes near-camera anchor objects.
Midground usually contains the main action or main subject.
Background deepens the world and supports narrative.

DENSITY: every scene should feel production-designed.
ABSOLUTE: never solve multi-location narration with split-screen, collage,
dollhouse cutaway, or symbolic cross-section unless source explicitly asks.

SHOT-TYPE GUIDANCE
Use the camera scale from the LOCKED SCENE BREAKDOWN. For each scale, apply
the staging language from SHARED §9. Do not flatten every scene to the same
distance — let scale evolve while respecting the locked breakdown.

COLOR SCRIPT GUIDANCE
Let color mood evolve with story tension while staying historically grounded:
- routine life = muted natural tones;
- fear/uncertainty = cooler desaturated tones;
- night control = sodium yellow, weak tungsten, deep blue-grey ambient;
- decision/power interiors = restrained warm interiors with disciplined contrast;
- cyber monitoring = dim blue-grey screen light + weak institutional ceiling;
- investigation = cool screens, dull file-paper beige, muted desk-lamp warmth;
- domestic tension = low warm bulbs, phone glow, shadowed corners;
- hostile actor (SHARED §2.7) = dim side light, shadowed faces, muted earth
  tones, cold phone glow, rough interior darkness, no beauty lighting;
- aftermath / dread-heavy = drained dusty or cold subdued palette.
Never use decorative color for its own sake. Color must support story mood
and period realism.

ENVIRONMENTAL PHYSICS RULES
- smoke rises unless chemically heavy;
- dense gas hangs low;
- rain darkens surfaces and creates pooling or drips;
- dust settles on horizontal surfaces;
- fire creates smoke, ash, heat damage;
- cloth folds with gravity and body movement;
- metal reflects modestly unless intentionally polished;
- overcast light flattens contrast;
- indoor tungsten creates warm local pools;
- daylight direction must remain consistent;
- shadows must obey the stated light source;
- screens illuminate nearby faces and hands weakly, not as fantasy glow;
- no fantasy swirl effects; no magical/symbolic smoke unless story demands.

CHARACTER STAGING RULES
Whenever people are visible, describe: posture; hand placement; shoulder
tension; head angle; line of sight; body balance; micro-expression;
emotional state through behaviour only.

Prefer grounded cues such as: jaw clenched; shoulders tight; gaze lowered;
fingers braced on table edge; weight shifted uneasily; chin lifted in
defiance; stillness under pressure; fatigue visible in stance; guarded
expression; disciplined posture; one hand hovering over a keyboard; thumb
paused above a phone screen; tired eyes reflecting screen light; officers
leaning forward without theatrical gesture; hostile actors watching from
partial shadow; suspicious hands close to phones, bags, doors, or pockets;
radical handlers holding attention through stillness rather than dramatic
performance.

Do not express emotion through abstract labels alone. Emotion must be
visible through physical behaviour.

LIGHTING RULES
Every IMAGE PROMPT must include explicit lighting detail: source; direction;
quality; shadow behaviour; period realism.

Examples of acceptable specificity:
- "cold overcast late-afternoon natural light falling from upper right";
- "warm tungsten desk-lamp pool from lower left";
- "hard noon sunlight from upper center creating short downward shadows";
- "weak dawn light filtering through mist from frame right";
- "dim blue screen light from the monitor wall falling across faces and tabletops";
- "weak institutional ceiling tube light creating flat shadows under desks";
- "weak phone glow cutting across one side of a hostile actor's face,
  leaving the other side in dirty shadow";
- "single low bulb above a suspicious group creating harsh downward shadows
  under brows and cheekbones".

Always mention how shadows fall; where the light lands; whether ambient fill
is weak or soft; how reflective and matte surfaces respond differently;
how faces, cloth, concrete, metal, glass, plastic, screens, and paper react
under the stated light. No cinematic glow; no bloom; no fantasy shafts
unless naturally justified.

Hostile actor lighting — apply SHARED §2.7.

TEXTURE & MATERIALS RULES
Describe specific material surfaces relevant to the scene. Use concrete
details such as: chipped plaster; weathered timber; ring-stained teak; damp
concrete; cracked enamel paint; wrinkled canvas sandbags; dull gunmetal;
cotton tape around file jackets; rust on barricade hinges; brushed wool;
ceramic cup glaze; matte paper edges; dust-coated scooter paint; peeling
posters; woven felt; leather scuffing; scratched phone glass; smudged laptop
keys; frayed charging cables; worn plastic chairs; laminated ID cards; faded
notice boards; scuffed metal cabinets; dusty monitor bezels; creased file
folders; marker-stained whiteboards; cheap plastic phone covers; rough
kurta fabric; sweat-darkened collar edges; dusty sandals; loose electrical
tape; cracked floor tiles; rusted window grills.
Name actual surfaces, actual wear, actual finishes, actual physical aging.
Never keep this section generic.

ATMOSPHERE RULES
Describe the emotional field of the place in grounded environmental language:
- militarized routine;
- public fear normalized into daily life;
- administrative stillness before execution;
- closed-room strategic concentration;
- inhabited but emotionally withdrawn street;
- bureaucratic pressure under silence;
- restrained authority;
- social unease held beneath outward normalcy;
- digital suspicion building under institutional silence;
- late-night operational fatigue;
- ordinary domestic space disturbed by invisible threat;
- forensic patience under fluorescent light;
- radical manipulation hidden inside ordinary surroundings;
- hostile secrecy beneath routine conversation;
- criminal patience under low light;
- predatory calm inside a closed room;
- digital radicalisation pressure spreading through small devices;
- threat network discipline beneath silence.
Avoid vague terms like "dramatic", "epic", or "powerful" without grounded
situational context. Atmosphere must emerge from place, posture, silence,
emptiness, crowding, object arrangement, and withheld action.

NEGATIVE PROMPT RULES
Every IMAGE PROMPT must end with a NEGATIVE section drawing from SHARED
§11 (universal + hostile + Islamist militant + scene-specific lists),
PLUS the story-specific negatives from the STORY CONFIG BLOCK.

HOSTILE ACTOR PROMPTING EXAMPLES (in-line guidance, not output)

Avoid soft wording like:
"a calm man watching a phone screen"

Use grounded wording like:
"a hardened hostile recruiter figure watching a phone screen with narrowed
eyes, tense jaw, guarded posture, rough stubble, one side of his face cut by
weak blue phone light, fingers gripping the device too tightly, shoulders
angled away from the doorway"

Avoid:
"a gentle speaker addressing young men"

Use:
"a manipulative radical propagandist figure seated in partial shadow,
expression controlled but cold, one hand raised in a restrained commanding
gesture, younger men listening tensely from plastic chairs, no warmth in the
room, no devotional glow, no heroic framing"

Avoid:
"a group of men sitting peacefully"

Use:
"a suspicious group of men sitting in tense silence, bodies angled inward
around a phone, eyes lowered toward the screen, shoulders tight, hands close
to pockets or devices, faces half-lit by weak screen glow, posture secretive
and watchful"

DIGEN MOTION PROMPT RULES

Each scene must include exactly ONE DIGEN MOTION PROMPT.

CORE PRINCIPLE — CAMERA MOVES, SUBJECTS STAY STILL
The camera does ALL the motion work. Subjects, characters, hands, faces,
crowds, vehicles, and objects in the frame must remain still or near-still
during the 5-second clip. The motion prompt describes a controlled CAMERA
movement that gradually changes shot scale (wide aerial → medium → close)
while the subject holds the frozen pose from the IMAGE PROMPT.

Why this matters: Digen and similar image-to-video models deform faces,
hands, and bodies whenever the prompt describes subject motion. The safe
recipe is to keep the subject visually still and let the CAMERA approach it.
If the IMAGE PROMPT shows a man walking, the motion prompt must describe
the CAMERA moving forward following him — never the man's walk itself.

MANDATORY TWO-CLAUSE STRUCTURE — descent + push-in
Every motion prompt MUST follow this exact two-clause shape:

  Clause 1 — START + SLOW DESCENT/LOWER:
    "[Aerial / High aerial / Night aerial / Elevated / Doorway /
     Over-shoulder / Raised] view above [the location] slowly
     descending / lowering toward [the subject area];"

  Clause 2 — FORWARD PUSH + FINAL FRAMING ON SUBJECT:
    "camera [gently pushes forward / moves forward / pushes closer /
     settles] [revealing / following / closer to / holding on] [the
     final main subject or key visual anchor]."

The clip therefore evolves through shot scales: aerial establishing →
camera slowly descending → gradual push-in toward character or object →
close-up framing on the subject. This functions as a slow zoom, but it is
achieved via descent + dolly-in (not via a zoom lens) — so Digen does not
introduce zoom-lens artifacts.

Mandatory:
- minimal and controlled motion;
- ONE continuous camera move (descent + forward push counts as one);
- shot scale evolves from wider start to tighter end — never the reverse;
- end framing must rest on the main subject from the IMAGE PROMPT;
- subjects in the frame stay STILL — describe only camera motion;
- never use public figure names — apply SHARED §4;
- use role-based or composition-based language;
- motion supports the still image, never reinterprets it;
- never invent a second scene through motion;
- never travel between unrelated zones of the frame.

Forbidden subject motion (NEVER describe these in the motion prompt):
- a man walking, marching, or running across the frame;
- a crowd rushing, dispersing, or moving;
- vehicles driving past, arriving, or leaving;
- a character turning their head, raising a hand, gesturing, speaking, or
  reacting visibly;
- anyone entering or exiting the frame;
- hands picking up, placing down, or manipulating objects;
- doors opening, papers flying, smoke billowing, fire spreading, water
  flowing dynamically.
If the source narration implies any of these actions, render the action
as a frozen instant inside the IMAGE PROMPT, and let only the CAMERA
approach that frozen instant in the motion prompt.

Forbidden camera motion:
- fast arc; orbit; whip pan; crash zoom; strong crane sweep; dramatic spin;
- shaky handheld; complex multi-step camera choreography;
- aggressive lateral movement across large distances; excessive reframing;
- movement between unrelated zones; movement that invents a second scene;
- ASCENDING camera moves (rising up away from the subject);
- PULLING BACK from the subject (ending wider than it started);
- any move that does not end closer to the main subject than it started.

Preferred starting viewpoints (clause 1):
- Aerial view above [the location]
- High aerial view above [the location]
- Night aerial view above [the location]
- Elevated view above [the location]
- Elevated room view
- Raised view above [the table / desk / device / evidence]
- Over-shoulder view from behind [character archetype]
- Doorway view into [the room / space]

Preferred motion verbs:
slowly descending • slowly lowering • gently pushing forward • gently
moving closer • slowly approaching • pushing forward revealing • moving
forward toward • pushing closer to • moving forward following • softly
settling on • holding on • drifting slightly forward.

Length: ONE sentence with two clauses joined by `;` (start descent + push),
or up to two short sentences. Never a long cinematic paragraph. When
unsure, choose less camera motion.

Canonical examples — follow this exact pattern and rhythm:
- "Aerial view above the tea stall slowly descending toward the table;
  camera gently pushes forward revealing the documents and the two men
  speaking quietly."
- "Aerial view above the crowded bazaar slowly descending between cloth
  awnings; camera moves forward toward the walking man blending into the
  crowd."
- "Elevated view above the tea stall slowly lowering toward the seated
  group; camera gently pushes closer to the bearded man speaking calmly."
- "Aerial view above the bazaar slowly descending toward the seated man;
  camera gently pushes closer as the background subtly reveals the contrast
  of two worlds."
- "High aerial view above the bazaar slowly descending toward the dim tea
  stall; camera pushes forward revealing the lone man sitting in shadow."
- "Night aerial view above the bazaar slowly descending toward the lone
  walking figure; camera moves forward following him through the dim
  street."
- "Elevated room view slowly lowering toward the monitoring desk; camera
  gently pushes forward and settles on the officers watching the screen."
- "Over-shoulder view from behind the analyst slowly moving closer toward
  the paused video screen; camera holds on the tense hands near the
  keyboard."
- "Doorway view into the dim room slowly pushing inward; camera settles on
  the hostile recruiter's shadowed posture and the phone-lit faces around
  him."
- "Raised view above the evidence table slowly descending toward the seized
  phones; camera gently moves closer and holds on the arranged devices."

Note on the "walking man" / "lone walking figure" examples above: even
though the IMAGE PROMPT depicts a man mid-stride, the motion prompt
describes ONLY camera motion — "moves forward toward", "moves forward
following". The man's walk is implied as a frozen pose in the still
image; Digen interprets it correctly when only the camera is described as
moving. NEVER write "the man walks", "he steps forward", "she runs",
"they march" in the motion prompt.

Scene-specific guidance:
- bazaar / street / curfew / checkpoint / crowd → aerial or high-aerial
  start, slow descent toward main subject in the crowd, gentle forward
  push to close framing;
- domestic interiors → doorway or over-shoulder start, slow inward push,
  settle on phone-lit faces or seated group;
- desks / files / phones / laptops / object-led → raised view above the
  surface, slow descent, gentle push closer to the device;
- cyber monitoring / political / strategy rooms → elevated room view, slow
  descent toward the desk or screen, restrained forward push, hold on the
  officers or analyst;
- solitary figures → high aerial or elevated start, slow descent toward
  the figure, gentle forward push, hold on shadowed face or hands;
- hostile actor scenes → doorway, partial-shadow framing, over-shoulder,
  or aerial start; slow descent and push toward tense hands, guarded eyes,
  or the dim phone glow on the face.

OUTPUT FORMAT (STAGE C) — exact format per scene

--- Scene {X} / ~{TOTAL_ESTIMATED_SCENES} ---
Hindi line:
{exact Hindi line copied from the LOCKED SCENE BREAKDOWN}

IMAGE PROMPT
Scene {X}. {short scene context label}. Create a cinematic hand-drawn 2D matte painting set in {ERA}; {CITY}; {STATE OR REGION}; {COUNTRY}; {full single-line descriptive prompt with Foreground: Midground: Background: Lighting: Texture & Materials: Atmosphere: NEGATIVE:} ||

DIGEN MOTION PROMPT
{camera motion description}

STAGE C FORMATTING RULES
- no empty lines inside a scene block other than the structural breaks above;
- "Hindi line:" must match the LOCKED SCENE BREAKDOWN exactly (SHARED §6);
- never split, merge, rewrite, renumber, add, or remove scenes;
- never force multi-location content into one scene unless the locked scene
  itself supports one visible frame;
- never use public-figure real names outside "Hindi line:" (SHARED §4);
- "IMAGE PROMPT" must be on its own line; the actual prompt is exactly ONE
  single line; should normally exceed 3000 characters; ends with ` ||`;
- "DIGEN MOTION PROMPT" must be on its own line;
- never append `||` to DIGEN MOTION PROMPT or any other field;
- no bullet points; no commentary before or after.

MULTI-SCENE OUTPUT PROTECTION
When generating multiple scenes in one response, NEVER reduce IMAGE PROMPT
richness to fit more scenes.

ABSOLUTE LENGTH ENFORCEMENT
- every IMAGE PROMPT ≥ 3000 characters;
- never shorten, compress, summarize, or simplify any IMAGE PROMPT to fit
  more scenes;
- never trade richness for count;
- never produce lighter prompts for later scenes in a batch;
- Scene 1 and Scene N follow the same standard.

BATCH-SIZE BEHAVIOR
- if requested 10 scenes, generate up to 10 only if every IMAGE PROMPT can
  remain ≥ 3000 characters;
- if response length becomes a constraint, do NOT compress later scenes;
- stop after the last fully completed scene;
- never output a partially shortened scene to continue numbering.

FAILSAFE
- if any risk of forced shortening, generate fewer scenes and stop cleanly
  at the last complete scene;
- always prefer fewer full-quality scenes over more compressed scenes.
- when stopping early, indicate the next SCENE_RANGE the user should request
  in a fresh chat (e.g. user requested Scenes 1–10 but you only completed
  Scenes 1–7; tell them to run Scenes 8–10 in the next call). Do this on a
  single trailing line AFTER the last fully completed scene block, prefixed
  with `NEXT_RANGE:` — this is the ONLY non-scene line allowed.

QUALITY CONSISTENCY
- maintain identical descriptive depth, material specificity, lighting
  detail, composition density, environmental realism, and hostile-character
  severity across all scenes in the batch;
- detail must not decay as scene numbers increase.

NO-COMPRESSION (forbidden)
- shortening for batch reasons;
- medium-detail prompts for later scenes;
- reduced Foreground/Midground/Background/Lighting/Texture/Atmosphere detail;
- shorthand replacing grounded description;
- generic filler instead of scene-specific detail;
- removing hostile actor severity from later scenes.

PRIORITY ORDER (always)
1. exact LOCKED SCENE BREAKDOWN compliance;
2. full output format compliance;
3. minimum 3000-character IMAGE PROMPT per scene;
4. scene fidelity and visual richness;
5. hostile actor severity when relevant;
6. only then requested scene quantity.

QUALITY BAR — write like a storyboard artist who understands
- Indian and South Asian geography and architecture;
- institutional interiors;
- cyber monitoring spaces;
- intelligence and investigation rooms;
- domestic interiors;
- clothing and class distinctions;
- hostile actor staging;
- radicalisation and propaganda scenes without glorification;
- criminal and terror-network visual language without gore;
- 2D matte painting composition;
- cinematic depth;
- grounded emotional storytelling;
- historically believable environments.

Write with enough density that:
- the environment can be illustrated without guessing major missing details;
- emotional tone is carried by concrete world-building;
- hostile actors look unsafe, hardened, secretive, and threatening when
  relevant;
- each frame feels like a production-ready storyboard plate;
- each prompt is robust enough for high-quality image generation;
- the storyboard can realistically match narration audio in 5-second
  image-to-video clips.

STAGE C FINAL HARD RULES
- Use the LOCKED SCENE BREAKDOWN exactly.
- Do not segment the story again.
- Maintain strict chronological order.
- Generate exactly one IMAGE PROMPT and one DIGEN MOTION PROMPT per locked
  scene in the requested SCENE_RANGE.
- Keep IMAGE PROMPT as a single line.
- Every IMAGE PROMPT should normally exceed 3000 characters.
- Every IMAGE PROMPT line must end with a trailing ` ||` placed immediately
  after the last word of the NEGATIVE section.
- Use highly descriptive environment detail. Expand architecture, object
  density, lighting, textures, posture, clothing, and atmosphere fully.
- Keep recurring characters visually consistent (SHARED §5).
- Never use explicit names for public figures outside "Hindi line:"
  (SHARED §4).
- Hostile actors must look hardened, secretive, tense, suspicious,
  manipulative, dangerous, or operationally threatening through grounded
  body language and lighting (SHARED §2). Never gentle, innocent, heroic,
  glamorous, saintly, cute, harmless, or emotionally warm.
- Never glorify terrorists, extremists, criminals, radical handlers, or
  hostile propagandists.
- Never use readable religious text, extremist slogans, propaganda symbols,
  political party symbols, or identifying labels unless explicitly required
  by the source — and even then avoid readable detail.
- Never solve scene problems with split-screen, collage, or cross-section
  composition unless explicitly requested by the source.
- DIGEN MOTION PROMPT must stay restrained and use one calm primary move
  only — the mandatory two-clause descent + forward-push pattern.
- DIGEN MOTION PROMPT must describe ONLY camera motion. Subjects, hands,
  faces, crowds, vehicles, and objects must remain still in the prompt's
  language. Never write "the man walks", "she gestures", "they march",
  "the crowd rushes", or any subject-motion verb.
- DIGEN MOTION PROMPT must end CLOSER to the main subject than it started.
  No ascending moves, no pull-backs, no wider-at-end framings.
- When uncertain in motion design, choose less camera movement, not more.
- Never break the required output format. No commentary. No explanations.


================================================================================
PART 3 — INPUT SLOTS (fill these before sending)
================================================================================

STORY_CONFIG_BLOCK:
{Paste the STORY CONFIG BLOCK output from Stage A here.}

LOCKED_SCENE_BREAKDOWN:
{Paste the LOCKED SCENE BREAKDOWN output from Stage B here.}

CHARACTER_LIBRARY:
{Paste the same locked character library text used in Stage A and
Stage B (e.g. the contents of character.txt). Required for SHARED §12
to copy the LOCKED CHARACTER ANCHOR verbatim into IMAGE PROMPTs for
every scene whose "Library lock:" tag references a KEY. Leave blank
or write NONE if no library is supplied — Stage C will then fall back
to inference per SHARED §3, §4, §5.}

SCENE_RANGE:
{Example: "Scenes 1–10". Specify the scenes to generate IMAGE PROMPT + DIGEN MOTION PROMPT for in this call.}


================================================================================
PART 4 — TASK
================================================================================

Read the STORY_CONFIG_BLOCK, LOCKED_SCENE_BREAKDOWN, CHARACTER_LIBRARY,
and SCENE_RANGE above.
Apply PART 1 (SHARED LIBRARY) wherever referenced — including SHARED §12
to copy the LOCKED CHARACTER ANCHOR verbatim into the IMAGE PROMPT for
every scene whose "Library lock:" tag references a KEY found in the
CHARACTER_LIBRARY input slot.
Execute PART 2 (STAGE C SPEC).
Treat the STORY CONFIG BLOCK as authoritative for era, geography, character
roster, hostile profile, public-figure handling, color script, lighting,
anchor guidance, atmosphere, and story-specific NEGATIVE additions.
Treat the LOCKED SCENE BREAKDOWN as the final authority for scene count,
scene order, scene numbering, and Hindi line boundaries.
Output ONLY one IMAGE PROMPT + one DIGEN MOTION PROMPT per scene in the
requested SCENE_RANGE, in the exact format defined in PART 2.
If batch length forces stopping early, complete the last full scene and
add a single trailing `NEXT_RANGE: Scenes X–Y` line so the user knows
which range to request next. No other commentary or explanation.

================================================================================
END OF STAGE C FILE
================================================================================
