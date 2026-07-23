#!/usr/bin/env bash
# Start Chrome with remote debugging for library/flow_generate.py
#
# Uses a dedicated profile (~/.flow-playwright-chrome) so your main Chrome can stay open.
# First run: log into labs.google in the window that opens, open a Flow project, then run flow_generate.py
#
# Usage:
#   ./story-agent/start-flow-browser.sh
#   python3 library/flow_generate.py path/to/image-prompts-only.txt --start 1 --count 5

set -euo pipefail

PORT="${1:-9223}"
FLOW_URL="${2:-https://labs.google/fx/tools/flow/}"
AUTOMATION_DIR="${FLOW_CHROME_USER_DATA:-$HOME/.flow-playwright-chrome}"
MAIN_CHROME="${HOME}/Library/Application Support/Google/Chrome"
DEFAULT_PROFILE="${MAIN_CHROME}/Default"

pick_browser() {
  if [ -d "/Applications/Google Chrome.app" ]; then
    echo "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return
  fi
  echo "Google Chrome not found in /Applications" >&2
  exit 1
}

bootstrap_profile() {
  mkdir -p "${AUTOMATION_DIR}/Default"
  if [ ! -f "${AUTOMATION_DIR}/Local State" ] && [ -f "${MAIN_CHROME}/Local State" ]; then
    cp "${MAIN_CHROME}/Local State" "${AUTOMATION_DIR}/Local State"
  fi
  if [ ! -f "${AUTOMATION_DIR}/Default/Preferences" ] && [ -f "${DEFAULT_PROFILE}/Preferences" ]; then
    cp "${DEFAULT_PROFILE}/Preferences" "${AUTOMATION_DIR}/Default/Preferences"
  fi
  for f in Cookies "Login Data" "Network Persistent State"; do
    if [ ! -f "${AUTOMATION_DIR}/Default/${f}" ] && [ -f "${DEFAULT_PROFILE}/${f}" ]; then
      cp "${DEFAULT_PROFILE}/${f}" "${AUTOMATION_DIR}/Default/${f}" 2>/dev/null || true
    fi
  done
}

BIN="$(pick_browser)"
bootstrap_profile

echo "Flow automation Chrome"
echo "  Profile: ${AUTOMATION_DIR}"
echo "  CDP:     http://127.0.0.1:${PORT}"
echo "  URL:     ${FLOW_URL}"
echo ""
echo "Leave this window open. Open a Flow project, then run:"
echo "  python3 library/flow_generate.py <image-prompts-only.txt> --cdp-url http://127.0.0.1:${PORT} --start 1 --count 5"

exec "$BIN" \
  --remote-debugging-port="${PORT}" \
  --user-data-dir="${AUTOMATION_DIR}" \
  "${FLOW_URL}"
