---
name: copy-to-playwright
description: >-
  Copy a cms-generate-stories story folder into playright-automation for image
  generation: prompts/prompt.txt → prompt/<slug>.txt and images/<slug>/.
  Use when the user says copy to playwright, copy in playwright, copy in
  playwrite, prepare playwright, sync to playwright, or wants prompt.txt ready
  for digen/playwright automation.
---

# Copy to Playwright

Sync a CMS story folder into the playwright automation project.

## Run immediately

Do not explain first — run the script, then report paths created.

```bash
./cms-generate-stories/prepare-playwright.sh "<story-folder>"
```

Run from repo root. Request `all` permissions if writes outside the repo are blocked.

## Resolve `<story-folder>`

Use the first match:

1. **Explicit path** the user gave (absolute or relative)
2. **Slug only** (e.g. `154-balochistan-s-independence-movement`) → search:
   `cms-generate-stories/*/<slug>/`
3. **Open / recent file** under `cms-generate-stories/<type>/<slug>/` → use that `<slug>` folder
4. **Ask** only if none of the above resolves to one folder

## What the script does

| Source | Destination |
|--------|-------------|
| `<story-folder>/prompts/prompt.txt` | `/Users/averma/project/automation/playright-automation/prompt/<slug>.txt` |
| (new folder) | `/Users/averma/project/automation/playright-automation/images/<slug>/` |

`<slug>` = basename of the story folder (e.g. `154-balochistan-s-independence-movement`).

## After running

Confirm both outputs exist. If `prompts/prompt.txt` is missing, tell the user the pipeline has not finished step 4 yet.

## Example

User: *copy 154-balochistan to playwright*

```bash
./cms-generate-stories/prepare-playwright.sh \
  "/Users/averma/project/research-story-17thmay-automation/cms-generate-stories/general/154-balochistan-s-independence-movement"
```
