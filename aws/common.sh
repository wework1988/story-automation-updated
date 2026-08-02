#!/usr/bin/env bash
# Shared config and helpers for cms-generate-stories S3 sync.
#
# S3 mirrors the contents of cms-generate-stories/ exactly:
#
#   Local:  cms-generate-stories/general/bladirmir-putin/script/FULL_STORY.txt
#   S3:     s3://bucket/general/bladirmir-putin/script/FULL_STORY.txt

AWS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMS_S3_REPO_ROOT="$(cd "${AWS_DIR}/.." && pwd)"
CMS_S3_DIR="${CMS_S3_REPO_ROOT}/cms-generate-stories"
CMS_S3_BUCKET="${S3_BUCKET:-mystorybucket-361103953046-us-east-1-an}"
CMS_S3_REGION="${AWS_REGION:-us-east-1}"

cms_s3_check_aws() {
  if ! command -v aws >/dev/null 2>&1; then
    echo "aws CLI not found. Install: brew install awscli" >&2
    exit 1
  fi

  if ! aws sts get-caller-identity --region "${CMS_S3_REGION}" >/dev/null 2>&1; then
    echo "AWS credentials not configured. Run: aws configure" >&2
    exit 1
  fi
}

cms_s3_normalize_story_path() {
  local path="$1"
  [[ -z "${path}" ]] && printf '%s' "" && return 0

  if [[ "${path}" == /* ]]; then
    if [[ ! -d "${path}" ]]; then
      echo "Story folder not found: ${path}" >&2
      return 1
    fi
    path="$(cd "${path}" && pwd)"
    if [[ "${path}" == "${CMS_S3_DIR}"/* ]]; then
      path="${path#"${CMS_S3_DIR}/"}"
    elif [[ "${path}" == "${CMS_S3_DIR}" ]]; then
      path=""
    else
      echo "Path must be inside cms-generate-stories/: ${1}" >&2
      return 1
    fi
  fi

  path="${path#/}"
  path="${path%/}"

  if [[ "${path}" == cms-generate-stories ]]; then
    path=""
  elif [[ "${path}" == cms-generate-stories/* ]]; then
    path="${path#cms-generate-stories/}"
  fi

  printf '%s' "${path}"
}

cms_s3_resolve_paths() {
  local story_path="$1"

  if [[ -n "${story_path}" ]]; then
    CMS_S3_LOCAL="${CMS_S3_DIR}/${story_path}"
    CMS_S3_REMOTE="s3://${CMS_S3_BUCKET}/${story_path}/"
  else
    CMS_S3_LOCAL="${CMS_S3_DIR}/"
    CMS_S3_REMOTE="s3://${CMS_S3_BUCKET}/"
  fi
}

cms_s3_upload_excludes=(
  --exclude ".DS_Store"
  --exclude "*/.DS_Store"
  --exclude "*/*/.DS_Store"
  --exclude "*.log"
  --exclude "*.zip"
  --exclude "*/*.zip"
  --exclude "*/*/*.zip"
  --exclude "*/*/*/*.zip"
  --exclude "*/*/*/*/*.zip"
  --exclude "*.textClipping"
  --exclude "*-packet/*"
)

cms_s3_show_mapping() {
  cat <<EOF
Structure (1:1 mirror of cms-generate-stories/):

  Local:  ${CMS_S3_DIR}/general/bladirmir-putin/script/FULL_STORY.txt
  S3:     s3://${CMS_S3_BUCKET}/general/bladirmir-putin/script/FULL_STORY.txt
EOF
}

cms_s3_upload_story() {
  local story_path="$1"
  local dry_run="$2"

  cms_s3_resolve_paths "${story_path}"

  if [[ ! -d "${CMS_S3_LOCAL}" ]]; then
    echo "Story folder not found locally: ${CMS_S3_LOCAL}" >&2
    return 1
  fi

  local sync_args=(
    "${CMS_S3_LOCAL}"
    "${CMS_S3_REMOTE}"
    --region "${CMS_S3_REGION}"
    "${cms_s3_upload_excludes[@]}"
  )

  if [[ "${dry_run}" -eq 1 ]]; then
    sync_args+=(--dryrun)
  fi

  echo "Source:  ${CMS_S3_LOCAL}"
  echo "Dest:    ${CMS_S3_REMOTE}"
  cms_s3_show_mapping
  echo "Mode:    $([[ "${dry_run}" -eq 1 ]] && echo 'dry-run upload' || echo 'upload (new/changed files only)')"
  echo "Skipped: *-packet/, all *.zip files, .DS_Store, *.log"
  echo "Note:    files already on S3 with same size/date are not re-uploaded"
  echo ""

  aws s3 sync "${sync_args[@]}"
  echo ""
}

cms_s3_download_story() {
  local story_path="$1"
  local dry_run="$2"

  cms_s3_resolve_paths "${story_path}"
  mkdir -p "${CMS_S3_LOCAL}"

  if ! aws s3 ls "${CMS_S3_REMOTE}" --region "${CMS_S3_REGION}" >/dev/null 2>&1; then
    echo "Not found on S3: ${CMS_S3_REMOTE}" >&2
    return 1
  fi

  local sync_args=(
    "${CMS_S3_REMOTE}"
    "${CMS_S3_LOCAL}"
    --region "${CMS_S3_REGION}"
  )

  if [[ "${dry_run}" -eq 1 ]]; then
    sync_args+=(--dryrun)
  fi

  echo "Source:  ${CMS_S3_REMOTE}"
  echo "Dest:    ${CMS_S3_LOCAL}"
  cms_s3_show_mapping
  echo "Mode:    $([[ "${dry_run}" -eq 1 ]] && echo 'dry-run download' || echo 'download (new/changed files only)')"
  echo ""

  aws s3 sync "${sync_args[@]}"
  echo ""
}
