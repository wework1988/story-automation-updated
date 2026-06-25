#!/usr/bin/env bash
# Start a Chromium browser with remote debugging so the story agent can attach
# to your existing login session (claude.ai).
#
# Usage:
#   1. Quit Chrome / Edge / Brave completely
#   2. ./story-agent/start-debug-browser.sh
#   3. Log into claude.ai if needed (session usually persists)
#   4. ./story-agent/run.sh
#
# Keep this browser window open while the agent runs.

set -euo pipefail

PORT="${1:-9222}"
URL="${2:-https://claude.ai/new}"
USER_DATA="${HOME}/Library/Application Support/Google/Chrome"

pick_browser() {
  if [ -d "/Applications/Google Chrome.app" ]; then
    echo "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    USER_DATA="${HOME}/Library/Application Support/Google/Chrome"
    return
  fi
  if [ -d "/Applications/Microsoft Edge.app" ]; then
    echo "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    USER_DATA="${HOME}/Library/Application Support/Microsoft Edge"
    return
  fi
  if [ -d "/Applications/Brave Browser.app" ]; then
    echo "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    USER_DATA="${HOME}/Library/Application Support/BraveSoftware/Brave-Browser"
    return
  fi
  echo "No Chrome/Edge/Brave found in /Applications" >&2
  exit 1
}

BIN="$(pick_browser)"

echo "Starting browser with remote debugging on port ${PORT}"
echo "Profile: ${USER_DATA}"
echo "Leave this window open, then run: ./story-agent/run.sh"

exec "$BIN" \
  --remote-debugging-port="${PORT}" \
  --user-data-dir="${USER_DATA}" \
  "${URL}"
