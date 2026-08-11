# Scene Pipeline Findings — Missing / Wrong Hindi Lines

**Date:** 2026-08-11  
**Re-verified against on-disk artifacts:** 2026-08-11  
**Stories checked:**
- `cms-generate-stories/general/128-khamnai-chatgpt-version-shared`
- `cms-generate-stories/general/129-alcatraz-prison-story`
- `cms-generate-stories/general/130-naxali-india`

## Pipeline path

```
FULL_STORY.txt
  → Stage A  (output_config_*.md)
  → Stage B  (output_story_breakdown_*.md)   ← locked Hindi per scene
  → Stage C  (prompts/prompt.txt)           ← image/motion + Hindi
  → export_prompt_derivatives.py
  → scenes/scene.txt                        ← Hindi only (copied from prompt)
```

**Important:** Same scene **count** does **not** mean same Hindi **content**.  
Stage C can keep Scene 1…N while putting **wrong / shifted / duplicated** Hindi into those slots. Export then copies that into `scene.txt`.

---

## Summary table

| Story | FULL_STORY lines | Stage B | prompt / scene.txt | Main failure | Approx missing from scene.txt |
|-------|------------------|---------|--------------------|--------------|-------------------------------|
| **128 khamenei** | 319 | 394 headings / **333 unique** (61 dup numbers) | 333 | **Stage B parallel renumber** + Stage C drift | **~66** |
| **129 alcatraz** | 323 | 387 unique (clean) | 387 | **Stage C Hindi rewrite / duplicate** | **~10** |
| **130 naxali** | 277 | 337 unique (clean, **100% story coverage**) | 337 | **Stage C Hindi rewrite / shift** | **12** |

---

## Root causes

### A. Stage B parallel bug (clear code defect)

**Introduced:** 2026-07-23 commit `51a14e6` (`optimize: parallelize Stage B/C DeepSeek calls`)

In parallel Stage B, each slice gets:

```python
banner = stage_b_pipeline_split_banner(idx, seg_total, 0)  # always 0
```

So later slices are told to **start numbering at Scene 1** instead of continuing from prior slices. Merge keeps colliding scene numbers → later consumers effectively lose blocks.

**Hit hardest:** 128-khamenei (Aug 5 run, after Jul 23).

### B. Stage C Hindi not enforced (latent + worse after parallel)

Stage C template says copy Hindi **verbatim** from Stage B.  
Code only checks that **scene numbers exist**, not that Hindi matches Stage B.

**Default after Jul 23:** `stage_c_parallel_batches = 4`

**Hit:** 130-naxali, 129-alcatraz (Stage B OK; Stage C wrong).

### C. Export is faithful

`export_prompt_derivatives.py` copies `Hindi line:` from `prompt.txt` into `scene.txt`.  
If Stage C is wrong, `scene.txt` is wrong. Export is not the primary bug.

### Why it “was fine before”

- Before Jul 23: Stage B/C mostly **sequential**
- After Jul 23: parallel defaults + same missing Hindi validation → gaps more common
- Older stories (e.g. kandhar-hijack, Jul 18) were generated before that change

---

## Story 1 — `130-naxali-india`

### Status

| Artifact | Verdict |
|----------|---------|
| `script/FULL_STORY.txt` | Source of truth |
| `scenes/output_story_breakdown_naxali-india.md` | **Correct** — 337 scenes, no dup numbers, **0 missing** story lines |
| `prompts/prompt.txt` | **Wrong Hindi** on many scenes (77 B≠C mismatches) |
| `scenes/scene.txt` | Same as prompt — **12 FULL_STORY lines absent** |

### Missing from prompt / scene (present in breakdown Scenes 62–74)

These FULL_STORY lines (file L105–L129 block) are **gone** from `prompt.txt` / `scene.txt`:

- L105 — हिंसा को राजनीतिक प्रक्रिया का मुख्य साधन…
- L107 — विमल किसान transition…
- L109 — हमारे स्रोतों में एक किसान का नाम विमल किसान दिया गया है।
- L111–L129 — Vimal land dispute, 1967 Naxalbari, 23 May police clash  

Later callbacks (“विमल किसान के उदाहरण पर वापस…”) still appear near the end of `scene.txt`, but the **original introduction block** is missing.

### Example: same scene number, different Hindi

| Scene | Stage B (correct) | Stage C / scene.txt (wrong) |
|------:|-------------------|-----------------------------|
| 62 | इस विचार की सबसे खतरनाक बात सिर्फ हिंसा नहीं थी… | पार्टी मुख्य विपक्षी ताकतों में आती है और 1957 में केरल में सरकार बनाती है। |
| 64 | हमारे स्रोतों में एक किसान का नाम विमल किसान दिया गया है। | लेकिन पार्टी के भीतर हर कोई इससे सहमत नहीं था। |
| 71 | 1967 में नक्सलबाड़ी और आसपास के इलाके में किसान आंदोलन उग्र होता है। | माओ की सशस्त्र रणनीति की तरफ झुकते हैं। |
| 74 | 23 मई को पुलिस के साथ झड़प में एक पुलिस अधिकारी की मौत होती है। | इनमें विचार यह था कि ग्रामीण सत्ता-संबंधों को हिंसक तरीके से तोड़ा जाए। |
| 75 | इसके बाद पुलिस फायरिंग में… | इसके बाद पुलिस फायरिंग में… (**matches**) |

**Visible jump:** Scene 74 → 75 skips the Naxalbari buildup even though breakdown has it.

### Extra issues

- Duplicate Hindi in scene.txt: Scenes **164/165**, **271/277**

### Fix for this story

1. Do **not** redo Stage B (already correct).
2. Overwrite every `Hindi line:` in `prompt.txt` from breakdown Scene N.
3. Re-export → refresh `scene.txt` (+ image-prompt derivatives if needed).
4. Regen audio/images only for repaired scenes if already generated.

---

## Story 2 — `129-alcatraz-prison-story`

### Status

| Artifact | Verdict |
|----------|---------|
| Stage B breakdown | **Mostly correct** — unique scene numbers; missing lines exist in B |
| Stage C / scene.txt | **Hindi drift / duplicates** — 387 scene slots; ~10 story lines absent by content; ~12 duplicate Hindi lines |

### Examples

| Scene | Stage B (correct) | Stage C / scene.txt (wrong) |
|------:|-------------------|-----------------------------|
| 120 | जेल में रबर के रेनकोट मौजूद थे। | जेल में रबर के रेनकोट मौजूद थे। (**ok**) |
| 121 | उनकी गिनती उतनी सख्ती से नहीं होती थी जितनी औजारों की। | जेल में रबर के रेनकोट मौजूद थे। (**duplicate of 120**) |
| 235 | एक ही वस्तु, दो अलग निष्कर्ष। | जिसमें एंगलिन परिवार से जुड़े फोटो और संपर्क थे। (**wrong**) |
| 364 | और शवों का न मिलना जीवित बचने की गारंटी नहीं। | पानी में मिला सामान वास्तविक योजना का संकेत देता है… (**paraphrase/wrong**) |

### Typical missing FULL_STORY themes in scene.txt

- Raincoat count line (L106 / Scene 121 content)
- Morris guard pattern line
- “एक ही वस्तु, दो अलग निष्कर्ष” and following tide/raft reconstruction lines
- Closing “दोनों पक्षों के पास सवाल हैं…” style lines

### Fix for this story

Same as naxali: **inject Hindi from Stage B into prompt.txt**, then re-export. Stage B is usable.

---

## Story 3 — `128-khamnai-chatgpt-version-shared`

### Status

| Artifact | Verdict |
|----------|---------|
| Stage B breakdown | **Broken numbering** — 394 headings, only **333 unique**; **61 duplicate scene numbers** |
| Stage C / scene.txt | Inherits bad merge + further drift — **worst gap** (~66 missing story lines) |

### Stage B parallel symptom

**Scene 144 appears twice** in breakdown with different Hindi:

1. `दूसरी तरफ, इस बदलाव का अर्थ यह भी था कि युद्ध की एक पुरानी सीमा टूट रही थी।`
2. `एक दूसरे स्रोत के अनुसार अमेरिकी Tomahawk missiles ने anti-aircraft network को निशाना बनाया।`

Slice merge could not keep both timelines under unique numbers → large middle block of FULL_STORY drops from the usable scene list.

### scene.txt sequence gap (example)

| Scene | Hindi in scene.txt |
|------:|--------------------|
| 144 | दूसरी तरफ, इस बदलाव का अर्थ यह भी था कि युद्ध की एक पुरानी सीमा टूट रही थी। |
| 145 | इन तकनीकी विवरणों में पूर्ण सहमति नहीं है… |

Large FULL_STORY stretch around regime-survival / Trump Nov 2024 / June 2025 strike narrative is **missing or out of order**.

### Duplicate Hindi in scene.txt (examples)

| Scenes | Duplicated content (start) |
|--------|----------------------------|
| 136 / 137 | कमेंट में अभी केवल एक शब्द लिखिए — “टेक्नोलॉजी”… |
| 186 / 204 | इसी दौरान यमन के हूती Red Sea shipping पर हमले… |
| 187 / 205 | इससे एक साथ दो maritime chokepoints… |

### Sample missing FULL_STORY themes

- Trump Nov 2024 / Jan 2025 return
- June 2025 US–Israel strikes on Iranian targets
- Regime survival / Geneva / True Promise / Tomahawk-related beats (depending on merge survivor)

### Fix for this story

1. **Redo Stage B** with `STAGE_B_PARALLEL_CALLS=1` (or after code fix for banners).
2. Then redo Stage C (ideally with Hindi injection).
3. Re-export `scene.txt`.  
   Patching prompt alone is **not enough** — breakdown itself has colliding scene numbers.

---

## Recommended code fixes (pipeline)

1. **Stage B parallel:** pass correct `scenes_locked_through` per slice (or force sequential until fixed). Default safe: `STAGE_B_PARALLEL_CALLS=1`.
2. **Stage C post-process:** for each Scene N, **overwrite Hindi** from Stage B breakdown; fail/warn on mismatch; detect duplicate Hindi.
3. Optional: CLI flag to **repair existing** `prompt.txt` from breakdown without re-calling the LLM, then re-export.

### Immediate workaround (new runs)

```bash
STAGE_B_PARALLEL_CALLS=1 STAGE_C_PARALLEL_BATCHES=1 FORCE=1 MAX_STEP=4 ./general-story/run_with_params.sh
```

Still recommend Hindi-injection — sequential Stage C can still drift without enforcement.

---

## Quick decision guide

| Story | Trust Stage B? | What to rerun |
|-------|----------------|---------------|
| 130 naxali | **Yes** | Patch/repair Stage C Hindi → export |
| 129 alcatraz | **Yes** | Patch/repair Stage C Hindi → export |
| 128 khamenei | **No** (dup scene numbers) | Redo Stage B (serial) → Stage C → export |

---

## Related commits

| Date | Commit | Change |
|------|--------|--------|
| 2026-07-23 | `4bc8f11` | Checkpoint before storyboard speed optimization |
| 2026-07-23 | `51a14e6` | Parallel Stage B/C — **primary regression** |
| 2026-07-29 | `420d896` | Stage C fallback toggle + timing logs |
| 2026-08-02 | `1a27d26` | Stage C heading `~?` regex (minor) |
