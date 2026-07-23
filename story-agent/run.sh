#!/usr/bin/env bash
# Unified story agent: research transcripts + generate story by type.
#
# Default: opens claude.ai in YOUR browser (not Cursor CLI).
#
#   Terminal 1 — start Chrome with claude.ai (keep open):
#     ./story-agent/start-debug-browser.sh
#
#   Terminal 2 — run the agent:
#     ./story-agent/run.sh
#
# Other modes:
#   ./story-agent/run.sh --mode claude-code    # Cursor / Claude Code CLI
#   ./story-agent/run.sh --mode api            # ANTHROPIC_API_KEY
#   ./story-agent/run.sh --research-only
#   ./story-agent/run.sh --generate-only --research-dir research-storage-stories/FOLDER
#
# Setup:
#   pip install -r story-agent/requirements.txt
#   playwright install chromium

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 story-agent/story_agent.py "$@"
