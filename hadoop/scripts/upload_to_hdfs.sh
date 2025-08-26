#!/usr/bin/env bash
set -euo pipefail

# 1. locate script dir & project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"           # .../project-root/hadoop/scripts
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"      # .../project-root

# 2. local input directory (change to processed)
INPUT_DIR="$PROJECT_ROOT/data/wikipedia-ml"

# 3. target directory on HDFS
HDFS_DIR="/wikipedia-ml"

# 4. ensure local dir exists
if [ ! -d "$INPUT_DIR" ]; then
  echo "ERROR: local dir not found: $INPUT_DIR" >&2
  exit 1
fi

# 5. create target directory on HDFS (ignore if exists)
hdfs dfs -mkdir -p "$HDFS_DIR"

# 6. batch upload all files
for file in "$INPUT_DIR"/*; do
  echo "Uploading $(basename "$file") → $HDFS_DIR"
  hdfs dfs -put -f "$file" "$HDFS_DIR"
done

# 7. List upload results
echo "Upload complete. Files now in HDFS $HDFS_DIR:"
hdfs dfs -ls "$HDFS_DIR"
