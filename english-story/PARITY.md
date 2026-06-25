# Feature parity: `english-story/` vs `crime-section/` / `general-story/`

Same model as [`general-story/PARITY.md`](../general-story/PARITY.md): both packages run the **same** DeepSeek engine via a thin launcher. English-story **does not** fork `crime-section/helper/deepseek_pipeline.py`; `english-story/helper/deepseek_pipeline.py` sets `DEEPSEEK_CONFIG_PATH` and passes `--crime-root` so all paths resolve under `english-story/`.

| Package | Language / use |
|---------|----------------|
| `crime-section/` | Crime / horror narratives |
| `general-story/` | Hindi / Hinglish general documentaries |
| `english-story/` | English-language documentaries |

See `general-story/PARITY.md` for the full feature checklist (Stages 1–4, helpers, INI, etc.) — it applies here with paths swapped to `english-story/`.

## Placeholder contract

Stage templates must keep the markers and placeholders the engine expects (`PH_*`, `PART 3 — INPUT SLOTS`, etc.). Source of truth: constants and comments in `crime-section/helper/deepseek_pipeline.py`.
