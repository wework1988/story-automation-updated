# Drupal Worker — Write Story from YouTube (Pipeline 1)

Runs the **bullet-pointer pipeline** for CMS Story nodes:

```
YouTube URLs → transcripts → DeepSeek + bullet-pointers.txt
→ story_pointers.txt → v3 master prompt → Claude API → FULL_STORY.txt
→ sync to cms-generate-stories/ and/or Drupal
```

## Setup

```bash
pip install -r story-agent/requirements.txt
chmod +x drupal-worker/run_generate_story.sh
```

**Environment** (repo-root `.env`):

```bash
DEEPSEEK_API_KEY=...      # bullet extraction
ANTHROPIC_API_KEY=...     # story generation (--mode api, default)

# Optional — live Drupal push/pull
DRUPAL_BASE_URL=https://your-drupal-site.test
DRUPAL_API_KEY=...
```

## CMS folder layout (local mirror)

For node **127**, create:

```
cms-generate-stories/general/127-my-story-slug/
├── meta/
│   ├── drupal-node-id.txt      # 127
│   ├── story-type.txt          # general
│   ├── story-title.txt         # optional
│   ├── duration-minutes.txt    # 30
│   └── youtube-urls.txt        # one URL per line (2–6)
└── script/                     # filled by worker
    └── FULL_STORY.txt
```

**meta/youtube-urls.txt** example:

```
https://www.youtube.com/watch?v=VIDEO1
https://www.youtube.com/watch?v=VIDEO2
https://www.youtube.com/watch?v=VIDEO3
https://www.youtube.com/watch?v=VIDEO4
```

## Run from CMS admin (local worker)

When you click **Write story from YouTube** in CMS, point the button at:

```bash
./drupal-worker/run_generate_story.sh --node-id 127
```

The worker finds `cms-generate-stories/**/meta/drupal-node-id.txt` matching `127`, reads URLs, runs the pipeline, writes:

- `cms-generate-stories/.../script/FULL_STORY.txt`
- `script/story_pointers.txt`, `prompts/prompt.txt`, etc.
- `research-storage-stories/127-...-research/outputfinal/` (research cache)

## Run against live Drupal API

```bash
./drupal-worker/run_generate_story.sh --from-drupal --node-id 127
```

Expects Drupal endpoints from `docs/drupal-story-pipeline/SIMPLE-FLOW.md`:

- `GET /api/story-pipeline/stories/{id}`
- `PATCH /api/story-pipeline/stories/{id}`

## Step-by-step

```bash
# Transcripts only
./drupal-worker/run_generate_story.sh --node-id 127 --research-only

# + DeepSeek pointers
./drupal-worker/run_generate_story.sh --node-id 127 --pointers-only

# Prompt only
./drupal-worker/run_generate_story.sh --node-id 127 --prepare-only

# Full story (API — no browser)
./drupal-worker/run_generate_story.sh --node-id 127 --mode api
```

## Wire CMS button

Drupal admin button → shell out or queue job:

```bash
cd /path/to/research-story-17thmay-automation
./drupal-worker/run_generate_story.sh --node-id {{ node.id }}
```

Or POST to a queue; a daemon runs the same command with `--from-drupal`.
