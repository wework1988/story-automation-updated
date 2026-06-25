
================================================================================
STORYBOARD PIPELINE — STAGE C: ENGLISH IMAGE + MOTION PROMPT ENGINE
Story Doctor Version — Character-Lock Hardened / 3000+ Prompt / Original Format Safe
================================================================================

HOW TO USE THIS FILE WITH CHATGPT

1. Run Stage A and save the STORY CONFIG BLOCK.
2. Run Stage B and save the LOCKED SCENE BREAKDOWN.
3. Open a new ChatGPT chat for Stage C.
4. Copy this ENTIRE file and paste it as your first message.
5. At the very bottom, fill in the input slots:
      STORY_CONFIG_BLOCK:     <-- Stage A output
      LOCKED_SCENE_BREAKDOWN: <-- Stage B output
      CHARACTER_LIBRARY:      <-- same locked character library used in Stage A and Stage B
      SCENE_RANGE:            <-- example: Scenes 1–8
6. Send.
7. ChatGPT must return ONLY IMAGE PROMPT + DIGEN MOTION PROMPT for the requested SCENE_RANGE.
8. Repeat in fresh chats with new SCENE_RANGE values until all scenes are complete.

WHY BATCH BY SCENE_RANGE

Every IMAGE PROMPT must normally exceed 3000 characters.
A full story may contain 80–110 scenes.
ChatGPT cannot reliably generate all prompts in one call.

Recommended batch size:
- Safe: 5–8 scenes per call.
- Aggressive: 10 scenes per call.

If the response must stop early, complete the last full scene and add only:

NEXT_RANGE: Scenes X–Y

No other commentary.

PIPELINE POSITION

English Story
   ↓
Stage A — Story Config Engine
   produces: STORY CONFIG BLOCK
   ↓
Stage B — Scene Breakdown Engine
   produces: LOCKED SCENE BREAKDOWN
   ↓
>>> Stage C — English Image + Motion Prompt Engine <<<
   produces: IMAGE PROMPT + DIGEN MOTION PROMPT per locked scene

================================================================================
PART 0 — DISPATCHER
================================================================================

ACTIVE STAGE: C

Execute ONLY Stage C.

Your job:
- Read STORY_CONFIG_BLOCK.
- Read LOCKED_SCENE_BREAKDOWN.
- Read CHARACTER_LIBRARY if supplied.
- Read SCENE_RANGE.
- Generate one IMAGE PROMPT and one DIGEN MOTION PROMPT for each requested scene.
- Use STORY_CONFIG_BLOCK as authority for era, geography, character roster, hostile profile, public-figure handling, color script, lighting, anchor guidance, atmosphere, visual tone, negative prompt additions, and story-specific rules.
- Use LOCKED_SCENE_BREAKDOWN as authority for scene order, scene numbering, English line boundaries, scene context label, current story context, visual continuity anchor, location, subject, supporting elements, surrounding environment, camera scale, emotional tone, scene function, and Library lock.
- Use CHARACTER_LIBRARY as authority for locked character visual identity.
- For every scene in SCENE_RANGE whose Library lock references a neutral character ID, copy the matching LOCKED CHARACTER ANCHOR verbatim into the IMAGE PROMPT.
- Treat Library lock propagation as mandatory identity plumbing.
- Apply safety-net lock resolution if Stage B missed a Library lock but the English line, main subject, current story context, or visual continuity anchor unambiguously points to one locked character in CHARACTER_LIBRARY.
- Output ONLY IMAGE PROMPT + DIGEN MOTION PROMPT for requested scenes.

Do NOT:
- re-segment scenes;
- renumber scenes;
- add scenes;
- remove scenes;
- rewrite English lines;
- paraphrase English lines;
- translate English lines;
- add commentary;
- explain reasoning;
- summarize;
- output scenes outside SCENE_RANGE;
- print Library lock IDs inside IMAGE PROMPT;
- print Library lock IDs inside NEGATIVE section;
- print Library lock IDs inside DIGEN MOTION PROMPT;
- print real public figure names outside the English line;
- create exact real-person likeness prompts;
- change the required output format.

================================================================================
PART 1 — GLOBAL VISUAL STYLE LOCK
================================================================================

Every IMAGE PROMPT must use this visual language:

2D digital animated illustration;
cinematic hand-drawn 2D matte painting;
clean hand-drawn line art;
flat cel shading;
minimal texture;
simplified forms with strong readability;
documentary realism;
restrained stylisation;
region-accurate facial features;
historically grounded environments;
muted documentary color palette unless the scene clearly requires warmer or brighter tonal treatment;
clear foreground / midground / background layering;
production-designed composition;
frozen documentary film frame.

Always avoid:

photorealism;
ultra-realism;
3D render;
CGI;
ray tracing;
global illumination;
lens flare;
bokeh;
depth of field blur;
glossy CGI finish;
hyper-detailed pores;
HDR realism;
photo textures;
futuristic design unless era supports it;
neon colors unless era and setting support them;
watermark;
logo;
readable text overlay;
poster layout;
split-screen collage;
empty stage-like backgrounds;
generic office;
generic city;
generic crowd;
generic room.

The output must feel like serious animated documentary production art, not a poster, thumbnail, fantasy illustration, or AI stock image.

================================================================================
PART 2 — PUBLIC FIGURE AND NAME RULE
================================================================================

This applies to:
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
Real public-figure names may appear ONLY inside English line if the original Stage B English line already contains them.

Outside English line, never write:
- real public figure names;
- initials that clearly identify them;
- exact likeness instructions;
- readable nameplates;
- readable party symbols;
- readable official insignia;
- readable logos;
- identifying poster text;
- exact real-person likeness prompts.

Outside English line, convert public figures into role-based archetypes.

Use:
senior prime-ministerial figure;
senior home-ministerial figure;
senior national political strategist figure;
senior national security strategist figure;
senior military commander figure;
senior intelligence official figure;
senior police investigator figure;
senior opposition figure;
political analyst figure;
grassroots organiser figure;
border security official figure.

If a public figure is library-locked:
- use the locked anchor from CHARACTER_LIBRARY;
- never print the real name in IMAGE PROMPT;
- never print the character ID in IMAGE PROMPT;
- never ask for an exact real-person likeness;
- preserve archetype-only phrasing.

================================================================================
PART 3 — HOSTILE ACTOR VISUAL MENACE
================================================================================

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

Apply hostile coding ONLY when the story or STORY CONFIG BLOCK identifies the person/group as hostile, criminal, extremist, militant, handler, operative, propagandist, terror commander, violent conspirator, or suspect linked to hostile activity.

Do NOT apply hostile coding only because of:
religion,
ethnicity,
nationality,
beard,
skullcap,
prayer cap,
shalwar kameez,
kurta,
hijab,
mosque background,
poverty,
migration status,
regional clothing.

Ordinary civilians must remain ordinary civilians.

When a hostile actor appears as main subject or co-subject:
- the figure must visually read as dangerous within 1–2 seconds;
- the Foreground section must open with a hostile actor staging block before environmental details;
- the actor must not look like a regular passer-by, friendly shopkeeper, calm teacher, gentle uncle, soft civilian, or sympathetic victim.

Hostile actors must include multiple grounded menace cues:

FACE / GROOMING:
- hardened weathered face;
- tense jaw;
- tight mouth;
- shadowed or narrowed eyes;
- rough grooming or heavy beard where story context supports it;
- deep brow shadow;
- sun-worn or stress-worn skin.

EXPRESSION / GAZE:
- cold watchful stare;
- guarded sideways glance;
- narrowed controlled menace;
- low-lidded calculating gaze;
- expressionless but deliberate stillness;
- jaw locked in suppressed aggression.

BODY / POSTURE:
- shoulders forward;
- body angled away from light;
- coiled stillness;
- hand gripping phone, file, bag, or device too tightly;
- other hand near pocket, doorway, cloth bag, or hidden object;
- guarded posture near wall, shutter, doorway, corner, or exit.

COSTUME / SETTING:
- story-accurate muted clothing;
- worn practical fabric;
- dust, creases, sweat, travel wear, or harsh environment marks;
- headwear only where geography supports it;
- suspicious device, folded paper, cheap smartphone, cloth bag, hidden file, or operational object if supported by scene;
- harsh side light, weak phone glow, low bulb, tube light, or half-shadow.

Never describe hostile actors as:
gentle,
calm in a peaceful way,
soft-faced,
innocent,
kind-looking,
warm,
graceful,
saintly,
pure,
humble,
harmless,
charming,
heroic,
stylish,
beautiful,
charismatic,
sympathetic,
noble,
ordinary,
regular,
neutral civilian,
friendly,
approachable,
relaxed,
open posture,
working-class everyman,
unremarkable face in the crowd.

If a hostile actor description becomes soft, rewrite it before output.

================================================================================
PART 4 — CIVILIAN SEPARATION RULE
================================================================================

Ordinary civilians from the same religion, region, ethnicity, nationality, or clothing family as hostile actors must remain ordinary civilians.

Do not make ordinary Muslim, Hindu, Sikh, Christian, Jewish, Pakistani, Indian, Bangladeshi, Afghan, Kashmiri, Middle Eastern, Western, migrant, border-area, poor, rural, or working-class civilians look threatening unless the story identifies them as hostile.

Civilian tension can be shown through:
- worry;
- confusion;
- fear;
- exhaustion;
- waiting;
- uncertainty;
- crowd pressure;
- ordinary clothing;
- family belongings;
- tired faces;
- checkpoint anxiety;
- public reaction.

Civilian tension must NOT become hostile coding unless the story demands it.

================================================================================
PART 5 — REGION / ORIGIN / ROLE VISUAL MAPPING
================================================================================

For every recurring character, group, crowd, or hostile actor, visual styling must come from:

origin + region + era + class + role + ideology + story context.

Detect and apply:

GEOGRAPHIC ORIGIN:
country,
state/province,
region,
city/town/village,
border region,
diaspora/foreign location.

ETHNO-REGIONAL VISUAL CONTEXT:
South Asian Indian,
Pakistani Punjabi,
Pakistani Pashtun / KPK / tribal belt,
Afghan / Taliban-style border region,
Kashmiri,
Bengali,
Middle Eastern,
Western,
mixed,
unknown.

ROLE CATEGORY:
ordinary civilian,
family member,
journalist,
police officer,
military officer,
intelligence official,
politician/public figure,
cyber analyst,
hostile actor,
terror commander,
extremist recruiter,
radical propagandist,
criminal operative,
handler,
suspect,
victim,
student,
crowd.

IDEOLOGICAL / ORGANISATIONAL CONTEXT:
Islamist militant,
Pakistan-based militant network,
Taliban-style militant,
separatist militant,
criminal gang,
cyber propaganda network,
political group,
official state actor,
neutral civilian,
unknown.

Never infer ideology from religion or clothing alone.
Never hostile-code a civilian without source support.

================================================================================
PART 6 — CHARACTER CONSISTENCY ENGINE
================================================================================

For all recurring characters, keep stable:

age range;
body build;
face shape;
skin tone;
hairstyle;
hairline;
facial hair;
glasses;
clothing family;
profession/status cues;
emotional baseline;
posture language;
role aura.

If the same character appears across scenes, maintain the same visual identity.

Allowed changes:
- lighting;
- camera angle;
- emotion intensity;
- location;
- era-appropriate clothing variation;
- age variation if the scene is flashback or future;
- visible stress, injury, fatigue, or disguise only if supported by story.

Not allowed:
- changing face shape;
- changing body build;
- changing hairline;
- changing glasses style;
- changing beard style without story reason;
- turning one character into another;
- borrowing traits from another locked character.

================================================================================
PART 7 — LOCKED CHARACTER LIBRARY RULE
================================================================================

CHARACTER_LIBRARY is authoritative when supplied.

Each locked character block may contain:

MATCH ALIASES — pipeline-only matching text.
LOCKED CHARACTER ANCHOR — copy verbatim every time.
NEGATIVE IDENTITY FIREWALL — traits that must not bleed in.
Optional IMMUTABLE FEATURES.
Optional WARDROBE / ERA VARIANTS.

For each scene:
1. Read the scene’s Library lock field from LOCKED_SCENE_BREAKDOWN.
2. If Library lock is NONE, use normal inference from STORY_CONFIG_BLOCK.
3. If Library lock contains one or more neutral character IDs, find each matching block in CHARACTER_LIBRARY.
4. Copy the matching LOCKED CHARACTER ANCHOR verbatim into IMAGE PROMPT.
5. Add scene-specific staging before or after the anchor.
6. Never edit inside the locked anchor.
7. Never shorten the locked anchor.
8. Never paraphrase the locked anchor.
9. Never translate the locked anchor.
10. Never replace the locked anchor with a generic phrase.
11. Never print the neutral ID in IMAGE PROMPT, NEGATIVE section, DIGEN MOTION PROMPT, scene label, or any generated field.

If the character library provides a matching age/era/wardrobe variant, choose the correct variant.
If no variant exists, preserve the locked anchor and add era/location/action adjustment after the anchor.

If a locked character is missing from CHARACTER_LIBRARY:
- do not print the raw character ID inside the IMAGE PROMPT;
- do not invent an anchor;
- use this warning only if absolutely necessary:

[LIBRARY MISS: locked character anchor not found — re-paste CHARACTER_LIBRARY]

Never expose the raw ID in generated prompt text.

================================================================================
PART 8 — STAGE C SAFETY-NET LOCK RULE
================================================================================

If Stage B missed a Library lock but the English line, Main subject, Current story context, Visual continuity anchor, or Supporting visual elements unambiguously points to one locked character in CHARACTER_LIBRARY:

- apply the matching locked character anchor as a safety-net;
- do not change scene numbering;
- do not rewrite LOCKED_SCENE_BREAKDOWN;
- do not print the ID;
- preserve the original English line.

Use safety-net only when the match is clear.
Do not guess if ambiguous.

================================================================================
PART 9 — LOCKED CHARACTER ANCHOR PLACEMENT RULE
================================================================================

Image models weight earlier tokens heavily.
Therefore, when a locked character is important to the scene, the anchor must appear early in the relevant layer.

If the locked character is the MAIN SUBJECT and the camera scale is:
medium shot,
close-up,
close-reaction,
over-shoulder,
extreme close-up,

place the copied LOCKED CHARACTER ANCHOR in Foreground.

If the locked character is the MAIN SUBJECT and the camera scale is:
wide establishing shot,
medium-wide shot,
aerial establishing shot,
high-angle wide shot,

place the copied LOCKED CHARACTER ANCHOR in Midground after the room/street/location layout sentence.

If the locked character is a SUPPORTING SUBJECT:
place the copied LOCKED CHARACTER ANCHOR in Midground.

If the locked character appears as:
photograph,
screen image,
reflection,
silhouette,
archive clipping,
newspaper image,
memory image,
partial hand,
partial face,
back view,

still include the locked anchor, but describe the visual form clearly.

Example:
“on a dim television screen, the same locked senior official appears as a muted archive image...”

Do not print the neutral ID.
Do not print real public name.

Scene-specific staging such as:
current action,
gaze direction,
hand placement,
props,
emotion,
lighting,
clothing adjustment,
age adjustment,
location pressure,
or story moment

must be added before or after the anchor.

Never edit inside the anchor.
Never bury the locked anchor after long environment detail when the character’s face consistency matters.

================================================================================
PART 10 — MULTI-CHARACTER IDENTITY FIREWALL
================================================================================

When CHARACTER_LIBRARY contains multiple locked characters, Stage C must keep each identity visually isolated.

A locked character may NEVER borrow, blend, inherit, or absorb another locked character’s:

face shape;
body build;
skin tone;
hairline;
hairstyle;
facial hair;
glasses;
eye shape;
nose;
jaw;
cheek structure;
clothing family;
posture language;
age presentation;
role aura;
public presence;
emotional baseline.

The scene setting, role context, or environment must NOT override locked identity.

Examples:
- A character in a rally scene must not become another rally-associated locked character.
- A character in a security room must not become another security-associated locked character.
- A character wearing formal clothing must not borrow another locked character’s face, beard, glasses, body type, or posture.
- A public leader, strategist, officer, criminal, victim, journalist, family member, or hostile actor must remain the exact locked person assigned by Library lock.

If Library lock contains only one ID:
- use only that character’s anchor;
- ignore all other CHARACTER_LIBRARY blocks for identity;
- all other character anchors are identity-forbidden for that scene.

If Library lock contains multiple IDs:
- each locked character must receive its own copied anchor;
- each must be staged as a separate visible person, screen image, photo, reflection, silhouette, or partial appearance;
- never merge two locked characters into one hybrid person.

================================================================================
PART 11 — ROLE SIGNAL VS IDENTITY SIGNAL
================================================================================

Stage C must separate role signals from identity signals.

ROLE SIGNALS include:
rally stage;
courtroom;
office;
war room;
security room;
police station;
family home;
street crowd;
prison;
hospital;
school;
media room;
border area;
religious place;
criminal hideout;
investigation table;
public speech setting;
official meeting setting.

IDENTITY SIGNALS come only from:
- the matched LOCKED CHARACTER ANCHOR;
- matched immutable features;
- matched wardrobe / era variant for that same character.

A role signal may change:
environment,
pose,
prop,
lighting,
surrounding crowd,
camera angle.

A role signal may NOT change:
face,
build,
hair,
facial hair,
glasses,
recognisable identity,
age presentation,
body type.

Library lock decides identity, not the environment.

================================================================================
PART 12 — IMAGE PROMPT HARD LENGTH RULE
================================================================================

Every IMAGE PROMPT must normally exceed 3000 characters.

Shorter prompts are allowed only when:
- the scene is genuinely minimal by nature; AND
- the image cannot be expanded honestly without inventing unsupported content.

Never sacrifice scene specificity for brevity.

Prompt richness is mandatory.

Expand:
environment layout;
architecture;
street fabric;
furniture placement;
object placement;
local materials;
clothing details;
hostile actor body language if relevant;
official posture language if relevant;
class markers;
weather traces;
dust;
decay;
maintenance level;
lighting behavior across surfaces;
emotional atmosphere through concrete physical detail;
institutional context;
object density;
foreground/midground/background layering;
visual continuity;
camera scale;
historical accuracy;
geographic accuracy.

Do not repeat identical descriptive blocks inside the same prompt.
Do not pad with generic adjectives.
Do not invent unsupported details merely to reach length.

================================================================================
PART 13 — COMPOSITION RULES
================================================================================

Every IMAGE PROMPT must contain:

1. clear layered depth;
2. meaningful Foreground;
3. meaningful Midground;
4. meaningful Background;
5. at least 7 concrete physical objects across the composition;
6. a world that feels inhabited, used, and believable;
7. visible wear, decay, dust, dampness, aging, or maintenance level appropriate to era and place;
8. realistic material behavior;
9. frozen film-frame staging;
10. no empty backgrounds;
11. no vague generic office / city / room / street;
12. one exact moment in time.

Foreground preferably includes near-camera anchor objects.
Midground usually contains the main subject or action.
Background deepens the story-world and supports narrative context.

Never solve multi-location narration with:
split-screen;
collage;
dollhouse cutaway;
symbolic cross-section;
floating map overlay;
poster montage;

unless the source explicitly asks for it.

================================================================================
PART 14 — SHOT TYPE GUIDANCE
================================================================================

Use the camera scale from LOCKED_SCENE_BREAKDOWN.

Do not flatten every scene to the same distance.

Apply the scene’s camera scale:

EXTREME WIDE ESTABLISHING SHOT:
show geography, scale, institutions, borders, city blocks, military base, crowd size, or landscape pressure.

WIDE ESTABLISHING SHOT:
show full room, corridor, street, border area, court exterior, command room, or media space with subjects integrated into environment.

MEDIUM-WIDE SHOT:
show body posture, surrounding objects, table layout, group dynamics, and location context.

MEDIUM SHOT:
show subject from waist/chest up with strong environment anchors.

OVER-SHOULDER SHOT:
show subject looking at map, phone, file, screen, doorway, crowd, or person.

CLOSE-UP:
show face, hands, object, document edge, phone glow, eye pressure, or decision moment while preserving story context.

EXTREME CLOSE-UP:
use only for critical objects or emotional pressure: map pin, hand near phone, eye behind glasses, file stamp without readable text, radio switch, tense jaw.

LOW-ANGLE SHOT:
use for institutional pressure, power, fear, scale, or authority.

HIGH-ANGLE SHOT:
use for vulnerability, surveillance, pressure, trapped geography, or strategic overview.

AERIAL ESTABLISHING SHOT:
use for border, city, convoy, camp, military base, geographic scale, or strategic map-like perspective.

TRACKING-STYLE FRAME:
still image should imply movement but motion prompt must still keep subject frozen.

STATIC DOCUMENTARY FRAME:
use for serious witness-like moments, court, office, aftermath, family, archival mood, or final CTA.

================================================================================
PART 15 — ABSTRACT LINE TRANSLATION
================================================================================

If the English line is abstract or conceptual, convert it into a grounded visual.

Examples of abstract lines:
“The pressure was not new.”
“The system was running out of room.”
“The silence meant something.”
“The real danger was hidden deeper.”
“This was no longer just a local issue.”

Do NOT use fantasy symbolism.
Do NOT use floating icons.
Do NOT use glowing abstract graphics.
Do NOT use split-screen metaphors.
Do NOT use poster-style symbolic montage.

Ground abstract lines through:
closed rooms;
maps;
files;
phones;
screens;
hands;
faces;
corridors;
empty chairs;
crowds waiting;
unreadable documents;
media cameras;
border roads;
command tables;
dim lamps;
old walls;
frozen faces;
security barricades;
silent vehicles;
rain on windows;
dusty evidence folders.

The visual must feel physically possible in the story world.

================================================================================
PART 16 — IMAGE PROMPT OUTPUT STRUCTURE
================================================================================

Stage C output must follow the original single-prompt structure.

Do NOT output IMAGE PROMPT as separate fields such as:
Style:
Foreground:
Midground:
Background:
Lighting:
Camera:
Mood:
Continuity:
Negative prompt:

Instead, output one full IMAGE PROMPT body after the IMAGE PROMPT heading.

The IMAGE PROMPT must contain the following internal labelled sections inside the single prompt body:

Foreground:
Midground:
Background:
Lighting:
Texture & Materials:
Atmosphere:
NEGATIVE:

The required output format per scene is:

--- Scene {X} / ~{TOTAL_ESTIMATED_SCENES} ---
English line:
{exact English line copied from the LOCKED SCENE BREAKDOWN}

IMAGE PROMPT
Scene {X}. {short scene context label}. Create a cinematic hand-drawn 2D matte painting set in {ERA}; {CITY}; {STATE OR REGION}; {COUNTRY}; {full single-line descriptive prompt with Foreground: ... Midground: ... Background: ... Lighting: ... Texture & Materials: ... Atmosphere: ... NEGATIVE: ...} ||

DIGEN MOTION PROMPT
{one short camera-only motion sentence with two clauses joined by a semicolon}

The IMAGE PROMPT should be one continuous prompt body, not a table and not a multi-field form.

The DIGEN MOTION PROMPT must be one short sentence, not a paragraph and not labelled sub-fields.

================================================================================
PART 17 — IMAGE PROMPT OPENING RULE
================================================================================

Every IMAGE PROMPT must begin like this:

Scene {X}. {short scene context label}. Create a cinematic hand-drawn 2D matte painting set in {ERA}; {CITY}; {STATE OR REGION}; {COUNTRY};

If exact city/region is unknown, use the most specific available setting from STORY_CONFIG_BLOCK or LOCKED_SCENE_BREAKDOWN.

Examples:
Scene 4. Court Pressure Entry. Create a cinematic hand-drawn 2D matte painting set in 2010; Ahmedabad; Gujarat; India;

Scene 12. Border Checkpoint Anxiety. Create a cinematic hand-drawn 2D matte painting set in the present day; India-Bangladesh border region; eastern India; India;

Scene 22. Command Room Decision. Create a cinematic hand-drawn 2D matte painting set in 2020s; secure national command room; New Delhi; India;

Do not use real public figure names in the scene context label.
Do not use raw Library lock IDs in the opening line.
Do not use readable text in the visual prompt.

================================================================================
PART 18 — FOREGROUND RULE
================================================================================

Foreground must include:
- main subject if close/medium/over-shoulder;
- near-camera objects;
- story-specific physical anchors;
- hand/object detail where appropriate;
- hostile actor first if hostile actor is main subject or co-subject.

Foreground must not be empty.

If the main subject is a hostile actor, open Foreground with the hostile actor description.

If the main subject is a locked character in close/medium scale, insert the locked anchor in Foreground.

If the main subject is an object, describe the object with material, placement, lighting, and story importance.

Foreground examples:
- edge of red-marked map;
- secure phone;
- file bundle;
- half-visible hand;
- desk lamp;
- old court railing;
- wet road surface;
- torn noticeboard;
- military radio;
- folded paper;
- cheap smartphone;
- closed shutter;
- archive photograph;
- microphone cluster without readable logos.

================================================================================
PART 19 — MIDGROUND RULE
================================================================================

Midground usually contains:
- main subject in wide/medium-wide shots;
- supporting characters;
- locked characters as supporting figures;
- operational action;
- table group;
- crowd structure;
- official meeting layout;
- hostile group arrangement;
- court / office / command room core activity.

If locked character is main subject in a wide or medium-wide frame, insert the locked anchor in Midground after the layout sentence.

If locked character is supporting subject, insert the locked anchor in Midground.

Do not bury a required locked anchor in Background unless the scene only shows a distant photo/screen/silhouette and Stage B supports that.

================================================================================
PART 20 — BACKGROUND RULE
================================================================================

Background must deepen the world.

It should include:
architecture;
street fabric;
walls;
windows;
corridors;
distant crowd;
security barricades;
border fence;
vehicles;
weather;
old infrastructure;
media lights;
unreadable signage shapes;
institutional surfaces;
military equipment silhouettes;
court passage;
command room screens with unreadable graphics;
city haze;
rural landscape;
riverbank;
checkpoint structure.

Do not include readable text, logos, slogans, party symbols, or exact insignia.

Background must not be empty or generic.

================================================================================
PART 21 — LIGHTING RULE
================================================================================

Lighting must be scene-specific.

Use:
natural daylight;
harsh noon light;
dim office light;
greenish fluorescent light;
sodium streetlight;
single low bulb;
phone glow;
screen glow;
rain-muted daylight;
dawn light;
dusty afternoon light;
court corridor light;
command room monitor glow;
press-camera flash as non-readable light;
stormy sky;
border floodlight.

Hostile actors:
use harder side light, phone under-light, tube light, low bulb, half-shadow, or doorway silhouette.

Officials:
use controlled institutional light, desk lamp, secure-room glow, low command-room light, court corridor light.

Aftermath:
use cold morning light, grey daylight, smoke haze, empty room light, or muted press-room light.

Avoid:
soft beauty lighting;
devotional glow;
heroic halo;
glamour lighting;
balanced studio light;
fantasy volumetric glow.

================================================================================
PART 22 — TEXTURE & MATERIALS RULE
================================================================================

Every IMAGE PROMPT must include Texture & Materials.

This section must describe:
surface quality;
fabric quality;
dust;
paper;
metal;
wood;
concrete;
plastic;
glass;
weathering;
age;
wear;
maintenance level;
environment-specific materials.

Examples:
worn paper fibers on old files;
scratched metal table edge;
faded cotton kurta fabric;
damp concrete wall;
dusty ceiling fan;
old wooden desk;
creased cloth bag;
rubber sandals;
matte plastic phone body;
cheap laminated ID card with unreadable details;
wet asphalt;
rusted barricade;
paint peeling from old corridor wall.

Do not use glossy CGI texture.
Do not use photorealistic pores.
Do not use hyper-detailed skin texture.
Do not use shiny fantasy materials.

================================================================================
PART 23 — ATMOSPHERE RULE
================================================================================

Every IMAGE PROMPT must include Atmosphere.

Atmosphere must describe emotional pressure through physical scene-world conditions.

Use:
tense silence;
institutional coldness;
public anxiety;
hidden operational pressure;
quiet menace;
border uncertainty;
command-room pressure;
aftermath stillness;
media glare;
legal pressure;
civilian exhaustion;
rain-muted fear;
dusty heat;
late-night secrecy;
stale office air;
held breath;
decision-heavy stillness.

Do not write vague atmosphere such as:
dramatic;
cinematic;
interesting;
important.

Atmosphere must connect to the scene function from Stage B.

================================================================================
PART 24 — CAMERA RULE
================================================================================

Camera must follow Stage B camera scale suggestion.

Describe:
framing;
angle;
distance;
composition;
what is centred;
what is partially obscured;
how foreground leads eye to subject;
how background supports the story.

Avoid:
lens jargon that implies photorealism;
depth-of-field blur;
bokeh;
cinematic lens artifacts;
overly dynamic action camera unless scene requires it.

Use documentary frame language:
static documentary frame;
slow visual pressure;
witness-like composition;
over-shoulder tension;
high-angle surveillance feel;
low-angle institutional pressure;
wide establishing geography;
medium shot with object anchors.

Camera description should be included naturally inside the IMAGE PROMPT body, before or around the labelled sections if needed.

================================================================================
PART 25 — NEGATIVE SECTION RULE
================================================================================

Every IMAGE PROMPT must include a NEGATIVE section.

Baseline NEGATIVE must include:

photorealistic, ultra-realistic, 3D render, CGI, ray tracing, glossy skin, hyper-detailed pores, HDR, lens flare, bokeh, depth of field blur, readable text, watermark, logo, poster layout, split-screen collage, modern objects if not era-appropriate, empty background, generic office, generic crowd, generic room, soft beauty lighting, glamorous pose, superhero pose, comedy expression, exaggerated cartoon style, exact real-person likeness, readable political symbols, readable religious slogans, propaganda logos.

Add hostile-actor negatives when hostile actors appear:

gentle face, innocent expression, warm smile, friendly smile, saintly glow, heroic pose, glamorous styling, cute look, sympathetic victim framing, soft devotional lighting, polished influencer appearance, fashionable villain glamour, harmless appearance, noble martyr framing, romanticised extremist look, ordinary man, regular passer-by, neutral civilian look, working-class everyman, unremarkable face in the crowd, documentary-flat hostile actor, blank neutral face, relaxed posture, open friendly stance, balanced studio lighting on the face, even soft daylight on the face, clean-shaven soft modern face unless story explicitly says disguise.

Add Islamist militant context negatives when relevant:

readable religious text, readable propaganda slogans, extremist logos, extremist flags, ordinary Muslim civilians portrayed as threatening, religion-only threat coding, ethnic stereotyping, gentle religious-teacher look for confirmed hostile extremist, saintly preacher framing for hostile recruiter, warm devotional glow on hostile figure, soft balanced light on militant face, modern fashionable dress on confirmed militant.

Add story-specific negative prompt additions from STORY_CONFIG_BLOCK.

Never include Library lock IDs in NEGATIVE.
Never include real public figure names in NEGATIVE.

================================================================================
PART 26 — END-OF-PROMPT TERMINATOR RULE
================================================================================

Every IMAGE PROMPT must end with a space followed by:

||

The `||` must be the final visible characters of the IMAGE PROMPT.

It must appear immediately after the last word of the NEGATIVE section.

Correct:
NEGATIVE: photorealistic, ultra-realistic, 3D render, CGI, readable text, watermark, logo, exact real-person likeness. ||

Never add `||` to:
English line,
DIGEN MOTION PROMPT,
scene label,
metadata,
NEXT_RANGE.

Never omit it.
Never replace it with another character.
Never put any text after it inside the IMAGE PROMPT.

================================================================================
PART 27 — DIGEN MOTION PROMPT RULES
================================================================================

Each scene must include exactly ONE DIGEN MOTION PROMPT.

CORE PRINCIPLE:
Camera moves.
Subjects stay still.

The DIGEN MOTION PROMPT must be one short sentence with two clauses joined by a semicolon.

It must not become a cinematic paragraph.
It must not introduce new action beyond the still IMAGE PROMPT.

Correct structure:
Raised view above the evidence table slowly descends toward the seized phones; camera gently moves closer and holds on the arranged devices.

Wrong:
Camera motion:
Subject motion:
Environmental motion:

Wrong:
The officer points at the map while people move behind him.

The motion prompt must describe ONLY slow, controlled camera movement.

People, faces, hands, crowds, vehicles, objects, smoke, fire, doors, papers, clothes, and background elements must remain still or near-still by default.

NO LIP-SYNC / NO MOUTH MOTION:
The DIGEN MOTION PROMPT must never instruct:
lips moving,
mouth moving,
speaking mouth,
talking face,
jaw movement,
cheeks moving,
eyes blinking,
eye movement,
eyebrow movement,
facial animation,
changing expression,
smile forming,
anger building,
face reacting.

Allowed:
a tiny still facial impression may be described only as a frozen hold:
“holding on a tense still face”
“settling on a composed expression”
“holding on a restrained expression”

The face must remain essentially still.

Safest motion pattern:

aerial / elevated / doorway / raised view
→ slowly descending / slowly lowering
→ gently pushing forward
→ settling closer on the main subject or key object.

The motion prompt should feel like a slow 5-second image-to-video camera move, not an action scene.

If IMAGE PROMPT shows a person walking, speaking, gesturing, reacting, handling an object, or mid-action, the MOTION PROMPT must treat it as a frozen pose and move only the camera toward it.

================================================================================
PART 28 — ABSOLUTE SUBJECT-STILLNESS RULE
================================================================================

Do NOT describe people:
speaking,
talking,
whispering,
walking,
turning,
reacting,
gesturing,
moving,
running,
marching,
entering,
exiting,
looking around,
picking up objects,
manipulating objects,
typing,
pointing,
opening doors,
driving,
fighting,
shouting with animated mouth,
crying with animated face.

Unless the locked scene explicitly requires that movement as the main visual beat.

Even when the IMAGE PROMPT depicts:
mid-speech,
mid-shout,
mid-argument,
mid-smile,
mid-reaction,
mid-walk,
mid-gesture,
tense action,

the MOTION PROMPT must treat that as a painted still frame and move only the camera.

================================================================================
PART 29 — MOTION CAMERA RULE
================================================================================

DIGEN MOTION PROMPT must end closer to the main subject than it started.

No ascending moves.
No pull-backs.
No wider-at-end framing.
No fast zoom.
No whip pan.
No spinning.
No dramatic dolly rush.
No random camera shake unless scene is action/climax and even then keep subtle.

Use:
slow push-in;
slow descent;
gentle forward drift;
controlled pan ending closer;
slow slide toward the key object;
subtle handheld documentary drift;
slow tightening from wide to medium;
slow tightening from medium to close;
gentle downward move from elevated view.

When uncertain, choose less camera movement, not more.

================================================================================
PART 30 — SCENE-SPECIFIC MOTION GUIDANCE
================================================================================

Use this motion logic depending on scene type:

Bazaar / street / curfew / checkpoint / crowd:
Start with aerial or high-aerial framing, slowly descend toward the main subject in the crowd, then gently push closer. The crowd must remain held still.

Domestic interiors:
Start from doorway, hallway, or over-shoulder framing, slowly push inward, then settle on phone-lit faces, seated group, table objects, or quiet domestic tension. People remain still.

Desks / files / phones / laptops / object-led scenes:
Start with raised view above the surface, slowly descend, then push closer to the device, document, file, phone, map, or object. Objects remain still.

Cyber monitoring / political / strategy rooms:
Start from elevated room view, slowly descend toward the desk, screen, map, or evidence board, then hold closer on officers, analysts, paused screens, or unreadable displays.

Solitary figures:
Start high or slightly elevated, slowly descend toward the figure, then gently push forward and hold on shadowed face, hands, posture, or silhouette. The figure remains still.

Hostile actor scenes:
Start from doorway, partial-shadow framing, over-shoulder, or raised view, then slowly descend and push toward tense hands, guarded eyes, dim phone glow, or shadowed posture. Do NOT describe the hostile actor speaking, walking, gesturing, or moving unless the locked scene specifically requires it.

Court / media / public pressure scenes:
Start wide from corridor or crowd pressure, slowly lower or push inward toward the central figure, camera cluster, file, doorway, or frozen face. Cameras do not flash unless described as still visual glare.

Military / command / map scenes:
Start above the command table or operations room, slowly descend toward red-marked map, file, radio, or central officer, then hold closer on the frozen decision point.

Aftermath scenes:
Start from wide stillness, slowly drift inward toward damaged object, empty chair, abandoned file, quiet corridor, smoke-hazed landscape, or frozen witness-like subject.

CTA / end-frame scenes:
Start slightly elevated over story-related symbolic objects, slowly descend and push closer to the central object arrangement; hold on the still documentary end-frame without readable text.

================================================================================
PART 31 — MOTION FINAL AUDIT
================================================================================

Before writing each DIGEN MOTION PROMPT, scan it and reject/rewrite it if it contains:

lip-sync;
mouth movement;
blinking;
facial animation;
expression change;
subject movement;
hands moving;
crowd movement;
vehicle movement;
object movement;
fast camera movement;
sudden movement;
action choreography;
walking;
speaking;
talking;
turning;
gesturing;
running;
marching;
fighting;
typing;
pointing;
opening doors;
animated smoke/fire/water unless extremely subtle and scene-supported.

The final prompt must describe only:
one very slow camera descent / lowering / controlled drift,
plus one gentle forward push ending closer to the frozen subject.

When uncertain, choose less motion.

================================================================================
PART 32 — OUTPUT FORMAT
================================================================================

Return only the requested scene prompts.

Use this exact format:

--- Scene {X} / ~{TOTAL_ESTIMATED_SCENES} ---
English line:
{exact English line copied from the LOCKED SCENE BREAKDOWN}

IMAGE PROMPT
Scene {X}. {short scene context label}. Create a cinematic hand-drawn 2D matte painting set in {ERA}; {CITY}; {STATE OR REGION}; {COUNTRY}; {full single-line descriptive prompt with Foreground: ... Midground: ... Background: ... Lighting: ... Texture & Materials: ... Atmosphere: ... NEGATIVE: ...} ||

DIGEN MOTION PROMPT
{one short camera-only motion sentence with two clauses joined by a semicolon}

Repeat for every scene in SCENE_RANGE.

Do not add:
notes,
analysis,
reasoning,
summary,
headings outside required format,
extra commentary,
multi-field motion prompts,
tables.

If batch length forces stopping early:
- complete the last full scene;
- add only:

NEXT_RANGE: Scenes X–Y

No other commentary.

================================================================================
PART 33 — FINAL QUALITY AUDIT
================================================================================

Before output, check every requested scene:

1. Scene range check:
Only scenes in SCENE_RANGE are generated.

2. English line check:
English line is copied exactly from LOCKED_SCENE_BREAKDOWN.

3. No scene mutation check:
Scene number, order, and line boundary are unchanged.

4. Required format check:
Each scene uses:
--- Scene {X} / ~{TOTAL_ESTIMATED_SCENES} ---
English line:
IMAGE PROMPT
DIGEN MOTION PROMPT

5. Image prompt structure check:
IMAGE PROMPT is one prompt body, not split into separate field blocks.

6. Internal section check:
IMAGE PROMPT includes Foreground, Midground, Background, Lighting, Texture & Materials, Atmosphere, and NEGATIVE.

7. Image prompt length check:
Every IMAGE PROMPT normally exceeds 3000 characters unless genuinely minimal.

8. Terminator check:
Every IMAGE PROMPT ends with space + `||`.

9. Terminator placement check:
`||` appears only at the end of IMAGE PROMPT, never in English line or DIGEN MOTION PROMPT.

10. Style check:
2D hand-drawn matte painting style is present.

11. No photorealism check:
Prompt rejects photorealism, 3D, CGI, HDR, lens blur, bokeh.

12. Composition check:
Foreground, midground, and background are meaningful.

13. Object density check:
At least 7 concrete physical objects appear across the composition unless scene is genuinely minimal.

14. Environment check:
No empty background, generic office, generic room, or generic city treatment.

15. Era check:
No wrong-era object, vehicle, clothing, infrastructure, or technology.

16. Geography check:
Region, architecture, clothing, and environment match STORY_CONFIG_BLOCK.

17. Public figure safety check:
No real public name outside English line.

18. Exact likeness check:
No exact real-person likeness instruction.

19. Library lock check:
If Library lock is present, matching locked anchor is copied verbatim.

20. Library ID check:
No raw Library lock ID appears inside IMAGE PROMPT, NEGATIVE, DIGEN MOTION PROMPT, or scene label.

21. Anchor placement check:
Locked anchor appears early in Foreground or Midground according to camera scale and subject role.

22. Anchor edit check:
Locked anchor is not paraphrased, trimmed, translated, or altered.

23. Multiple lock check:
If multiple locked characters appear, all anchors appear and are visually separated.

24. Identity firewall check:
No locked character borrows traits from another locked character.

25. Safety-net check:
If Stage B missed a clear lock, apply the anchor if unambiguous.

26. Hostile actor check:
Hostile actors look hardened, guarded, dangerous, and source-supported.

27. Hostile softness check:
No hostile actor is gentle, warm, innocent, ordinary, friendly, saintly, or sympathetic.

28. Civilian separation check:
Ordinary civilians are not hostile-coded because of religion, region, clothing, beard, skullcap, hijab, ethnicity, poverty, or nationality.

29. Negative prompt check:
Baseline negatives + story-specific negatives are included.

30. Motion format check:
DIGEN MOTION PROMPT is one short sentence with two clauses joined by a semicolon.

31. Motion prompt check:
DIGEN motion is camera-only by default.

32. No lip-sync check:
No mouth, lip, jaw, eye, blink, eyebrow, cheek, or facial animation.

33. Subject stillness check:
People, faces, hands, crowds, vehicles, and objects remain still unless explicitly required.

34. Motion direction check:
Camera ends closer to subject, no pull-back or wider-at-end move.

35. Motion brevity check:
DIGEN MOTION PROMPT is not a paragraph.

36. Output cleanliness check:
No commentary, no explanation, no extra text.

If any failure is found, fix it before output.

================================================================================
PART 3 — INPUT SLOTS (fill these before sending)
================================================================================

STORY_CONFIG_BLOCK:
{Paste the STORY CONFIG BLOCK output from Stage A here.}

LOCKED_SCENE_BREAKDOWN:
{Paste the LOCKED SCENE BREAKDOWN output from Stage B here.}

CHARACTER_LIBRARY:
{Paste the same locked character library text used in Stage A for THIS story.
The character folder/library may change per story; Stage C must detect the
available neutral character IDs from the supplied library and propagate those exact IDs into
"Library lock:" whenever the matching character appears, is referenced, is
implied, or appears as a younger/older/photo/silhouette/screen/reflection/memory
version. Leave blank or write NONE if no library is supplied — Stage B will then
emit no library locks and Stage C will fall back to inference per SHARED §3 and §5.}

SCENE_RANGE:
{Example: "Scenes 1–10". Specify the scenes to generate IMAGE PROMPT + DIGEN MOTION PROMPT for in this call.}

================================================================================
PART 4 — TASK
================================================================================

Read the STORY_CONFIG_BLOCK, LOCKED_SCENE_BREAKDOWN, CHARACTER_LIBRARY, and SCENE_RANGE above.

Execute Stage C only.

Apply all rules in this document.

Treat STORY_CONFIG_BLOCK as authoritative for:
era,
geography,
character roster,
hostile profile,
public-figure handling,
color script,
lighting,
visual anchors,
atmosphere,
story-specific NEGATIVE additions,
and Stage C guidance.

Treat LOCKED_SCENE_BREAKDOWN as authoritative for:
scene count,
scene order,
scene numbering,
English line boundaries,
scene context label,
current story context,
main subject,
supporting visual elements,
surrounding environment,
camera scale,
emotional tone,
scene function,
and Library lock.

Treat CHARACTER_LIBRARY as authoritative for:
locked character anchors,
immutable identity features,
negative identity firewalls,
and wardrobe/era variants.

For every scene in SCENE_RANGE:
- copy the English line exactly;
- generate one IMAGE PROMPT in the exact single-prompt format;
- generate one DIGEN MOTION PROMPT as one short sentence with two clauses joined by a semicolon;
- copy locked character anchors verbatim wherever Library lock applies;
- never print raw Library lock IDs inside IMAGE PROMPT, NEGATIVE section, or DIGEN MOTION PROMPT;
- never print real public figure names outside English line;
- ensure IMAGE PROMPT normally exceeds 3000 characters;
- ensure IMAGE PROMPT includes Foreground, Midground, Background, Lighting, Texture & Materials, Atmosphere, and NEGATIVE;
- ensure IMAGE PROMPT ends with space + `||`;
- ensure DIGEN MOTION PROMPT uses slow camera-only motion by default;
- ensure people, faces, hands, crowds, vehicles, and objects remain still unless explicitly required by the locked scene.

Output ONLY the requested scene prompts.

If batch length forces stopping early, complete the last full scene and add only:

NEXT_RANGE: Scenes X–Y

No other commentary or explanation.

================================================================================
END OF STAGE C FILE — ENGLISH STORY DOCTOR VERSION
================================================================================
