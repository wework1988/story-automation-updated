# AWS S3 — CMS Story Storage

Backup and restore `cms-generate-stories/` using S3.  
**S3 uses the same folder layout** as your local `cms-generate-stories/` directory.

**Bucket:** `mystorybucket-361103953046-us-east-1-an`  
**Region:** `us-east-1`

Console: [S3 bucket objects](https://us-east-1.console.aws.amazon.com/s3/buckets/mystorybucket-361103953046-us-east-1-an?region=us-east-1&tab=objects)

## Layout

```
aws/
  README.md           # this file
  common.sh           # shared config + sync helpers
  sync-to-s3.sh       # upload (local → S3)
  pull-from-s3.sh     # download (S3 → local)
```

## Folder structure (1:1 mirror)

| Local | S3 |
|-------|-----|
| `cms-generate-stories/general/` | `s3://bucket/general/` |
| `cms-generate-stories/crime/` | `s3://bucket/crime/` |
| `cms-generate-stories/english/` | `s3://bucket/english/` |
| `cms-generate-stories/god_story/` | `s3://bucket/god_story/` |

Story path format: `{type}/{story-slug}` (relative to `cms-generate-stories/`)

---

## Setup (one time)

```bash
brew install awscli
aws configure   # region: us-east-1
aws sts get-caller-identity
```

---

## Scripts

| Script | Direction | Purpose |
|--------|-----------|---------|
| `./aws/sync-to-s3.sh` | Local → S3 | Upload new/changed files |
| `./aws/pull-from-s3.sh` | S3 → Local | Restore deleted or missing stories |

### Upload

```bash
./aws/sync-to-s3.sh
./aws/sync-to-s3.sh crime/bank-robbery-114
./aws/sync-to-s3.sh .
./aws/sync-to-s3.sh --dry-run
```

**Never uploaded:** `*.zip`, `*-packet/`, `.DS_Store`, `*.log`

### Download

```bash
./aws/pull-from-s3.sh general/bladirmir-putin
./aws/pull-from-s3.sh --dry-run
```

---

## Environment overrides

```bash
export S3_BUCKET=my-other-bucket
export AWS_REGION=us-east-1
./aws/sync-to-s3.sh
```

---

## Notes

- **Incremental sync:** only new or changed files upload/download.
- **`cms-generate-stories/`** is gitignored; S3 is the backup for generated assets.
- Keep the bucket **private** unless your CMS needs public URLs.
