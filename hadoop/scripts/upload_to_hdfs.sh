#!/usr/bin/env bash
set -euo pipefail

# 1. 定位脚本目录 & 项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"           # .../project-root/hadoop/scripts
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"      # .../project-root

# 2. 本地待上传目录（改成 processed）
INPUT_DIR="$PROJECT_ROOT/data/wikipedia-ml"

# 3. HDFS 目标目录
HDFS_DIR="/wikipedia-ml"

# 4. 校验本地目录存在
if [ ! -d "$INPUT_DIR" ]; then
  echo "ERROR: local dir not found: $INPUT_DIR" >&2
  exit 1
fi

# 5. 在 HDFS 上创建目标目录（若已存在则忽略）
hdfs dfs -mkdir -p "$HDFS_DIR"

# 6. 批量上传所有文件
for file in "$INPUT_DIR"/*; do
  echo "Uploading $(basename "$file") → $HDFS_DIR"
  hdfs dfs -put -f "$file" "$HDFS_DIR"
done

# 7. 列出上传结果
echo "Upload complete. Files now in HDFS $HDFS_DIR:"
hdfs dfs -ls "$HDFS_DIR"
