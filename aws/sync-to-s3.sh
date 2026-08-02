#!/usr/bin/env bash
# Upload cms-generate-stories/ to S3 (new/changed files only).
#
# Usage:
#   ./aws/sync-to-s3.sh                         # sync entire tree
#   ./aws/sync-to-s3.sh crime/bank-robbery-114 # sync one story folder
#   ./aws/sync-to-s3.sh --dry-run               # preview
#
# Download from S3: ./aws/pull-from-s3.sh

set -euo pipefail

AWS_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=common.sh
source "${AWS_DIR}/common.sh"

DRY_RUN=0
STORY_PATH=""

usage() {
  cat <<EOF
Usage: ./aws/sync-to-s3.sh [OPTIONS] [STORY_PATH]

Upload cms-generate-stories/ → s3://${CMS_S3_BUCKET}/ (same folder layout)
Only uploads new or changed files — files already on S3 are not re-uploaded.

Download from S3: ./aws/pull-from-s3.sh [STORY_PATH]

Options:
  --dry-run   Show what would upload without copying
  -h, --help  Show this help

Examples:
  ./aws/sync-to-s3.sh
  ./aws/sync-to-s3.sh crime/bank-robbery-114
  ./aws/sync-to-s3.sh /path/to/cms-generate-stories/english/my-story
  ./aws/sync-to-s3.sh --dry-run

Never uploaded: *-packet/ folders, all *.zip files, .DS_Store, *.log
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

if [[ ! -d "${CMS_S3_DIR}" ]]; then
  echo "CMS folder not found: ${CMS_S3_DIR}" >&2
  exit 1
fi

cms_s3_check_aws
STORY_PATH="$(cms_s3_normalize_story_path "${STORY_PATH}")"
cms_s3_upload_story "${STORY_PATH}" "${DRY_RUN}"

echo "Done."
