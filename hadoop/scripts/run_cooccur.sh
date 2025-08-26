#!/usr/bin/env bash
set -euo pipefail

# 1. 脚本所在目录：project-root/hadoop/scripts
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 2. Hadoop 根目录：project-root/hadoop
HADOOP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 3. Streaming 代码目录：project-root/hadoop/streaming
STREAM_DIR="$HADOOP_DIR/streaming"

# 4. Mapper/Reducer 脚本的绝对路径
MAPPER="$STREAM_DIR/mapper_cooccur.py"
REDUCER="$STREAM_DIR/reducer_cooccur.py"

# 5. Stopwords 文件在项目根目录
STOPWORDS="$SCRIPT_DIR/../../stopwords.txt"

HDFS_INPUT="/wikipedia-ml"
HDFS_OUTPUT="/cooccur-outputs"

# 6. 自动判断 HADOOP_HOME
if [ -d "$HADOOP_DIR" ] && [ -f "$HADOOP_DIR/libexec/hdfs-config.sh" ]; then
    HADOOP_HOME="$HADOOP_DIR"
elif [ -d "$HOME/hadoop-3.3.3" ] && [ -f "$HOME/hadoop-3.3.3/libexec/hdfs-config.sh" ]; then
    HADOOP_HOME="$HOME/hadoop-3.3.3"
else
    echo "ERROR: Could not locate Hadoop libexec directory."
    exit 1
fi

echo "[INFO] Using Hadoop at $HADOOP_HOME"

# 7. Ensure mapper & reducer are executable
chmod +x "$MAPPER" "$REDUCER"

# 8. Clean previous output
hdfs dfs -rm -r -skipTrash "$HDFS_OUTPUT" 2>/dev/null || true

# 9. Run Hadoop Streaming
STREAMING_JAR="$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.3.3.jar"
echo "[RUN] Hadoop Streaming co-occur job"
"$HADOOP_HOME/bin/hadoop" jar "$STREAMING_JAR" \
  -input  "$HDFS_INPUT"/machine-learning*.txt \
  -output "$HDFS_OUTPUT" \
  -mapper "$MAPPER" \
  -reducer "$REDUCER" \
  -file "$MAPPER" \
  -file "$REDUCER" \
  -file "$STOPWORDS" \
  -verbose

# 10. List & preview results
echo "[RESULT] Listing $HDFS_OUTPUT"
hdfs dfs -ls -h "$HDFS_OUTPUT"

echo "[RESULT] Preview part-00000"
hdfs dfs -tail "$HDFS_OUTPUT"/part-00000
