#!/usr/bin/env bash
# Download cms-generate-stories/ from S3 (new/changed files only).
#
# Usage:
#   ./aws/pull-from-s3.sh                         # download entire tree
#   ./aws/pull-from-s3.sh general/bladirmir-putin # download one story
#   ./aws/pull-from-s3.sh --dry-run crime/bank-robbery-114

set -euo pipefail

AWS_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=common.sh
source "${AWS_DIR}/common.sh"

DRY_RUN=0
STORY_PATH=""

usage() {
  cat <<EOF
Usage: ./aws/pull-from-s3.sh [OPTIONS] [STORY_PATH]

Download s3://${CMS_S3_BUCKET}/ → cms-generate-stories/ (same folder layout)
Only downloads new or changed files (aws s3 sync).

Options:
  --dry-run   Show what would download without copying
  -h, --help  Show this help

Examples:
  ./aws/pull-from-s3.sh
  ./aws/pull-from-s3.sh general/bladirmir-putin
  ./aws/pull-from-s3.sh --dry-run crime/bank-robbery-114

Note: *-packet/ folders were never uploaded, so they cannot be restored from S3.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    *)
      if [[ -n "${STORY_PATH}" ]]; then
        echo "Unexpected extra argument: $1" >&2
        usage >&2
        exit 1
      fi
      STORY_PATH="$1"
      shift
      ;;
  esac
done

cms_s3_check_aws
STORY_PATH="$(cms_s3_normalize_story_path "${STORY_PATH}")"
cms_s3_download_story "${STORY_PATH}" "${DRY_RUN}"

echo "Done."
