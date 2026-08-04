#!/usr/bin/env bash
# CMS "Write story from YouTube" — bullet-pointer pipeline worker.
#
# Local CMS folder (node 127):
#   ./drupal-worker/run_generate_story.sh --node-id 127
#
# Live Drupal API:
#   export DRUPAL_BASE_URL=https://your-site.test
#   export DRUPAL_API_KEY=...
#   ./drupal-worker/run_generate_story.sh --from-drupal --node-id 127
#
# Requires: DEEPSEEK_API_KEY, ANTHROPIC_API_KEY (for --mode api)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 drupal-worker/generate_story.py "$@"
