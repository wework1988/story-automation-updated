# Optional upstream prompts (`crime-section/template/`)

`crime-section/` includes extra prompt files used outside the bifurcated DeepSeek loop:

- `story-writing`
- `story-writing-master-prompt`
- `title-thumbnailtext`

**General-story does not ship copies** so the package stays genre-neutral and smaller.

If you want the same files beside english-story runs, copy them from the sibling folder:

```bash
# From repo root
mkdir -p english-story/template
cp crime-section/template/story-writing crime-section/template/story-writing-master-prompt crime-section/template/title-thumbnailtext english-story/template/
```

Nothing in `english-story/helper/deepseek_pipeline.py` requires these paths; they are for manual or external workflows.
