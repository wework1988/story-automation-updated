#!/usr/bin/env bash
# Unified story agent: research transcripts + generate story by type.
#
#   ./story-agent/run.sh                              # run queue.txt
#   ./story-agent/run.sh --video-url URL --type crime --related 25
#   ./story-agent/run.sh --research-only              # transcripts only
#   ./story-agent/run.sh --prepare-only               # prompt only
#
# Setup:
#   pip install -r story-agent/requirements.txt
#   claude auth login

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 story-agent/story_agent.py "$@"
