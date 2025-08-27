#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# 1. Java 11 检测（复用 hadoop_setup.sh 中的逻辑）
###############################################################################
JAVA_11_FOUND=false

# macOS Homebrew installation path
if [ -d "/usr/local/opt/openjdk@11" ]; then
  export JAVA_HOME=/usr/local/opt/openjdk@11
  JAVA_11_FOUND=true
elif [ -d "/opt/homebrew/opt/openjdk@11" ]; then
  export JAVA_HOME=/opt/homebrew/opt/openjdk@11
  JAVA_11_FOUND=true

# Linux (Ubuntu/Debian)
elif [ -d "/usr/lib/jvm/java-11-openjdk-amd64" ]; then
  export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
  JAVA_11_FOUND=true
fi

if [ "$JAVA_11_FOUND" = false ]; then
  echo "ERROR: Java 11 not found. Spark 3.x 推荐使用 Java 11。"
  echo "请安装 OpenJDK 11："
  echo "  macOS (Homebrew): brew install openjdk@11"
  echo "  Ubuntu/Debian:    sudo apt install openjdk-11-jdk"
  exit 1
fi

echo "[INFO] Using Java at $JAVA_HOME"

###############################################################################
# 2. Spark 安装 & 环境变量
###############################################################################
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

SPARK_VERSION="3.3.1"
SPARK_ARCHIVE="spark-${SPARK_VERSION}-bin-hadoop3.tgz"
SPARK_URL="https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_ARCHIVE}"
SPARK_DIR="$PROJECT_ROOT/spark/spark-${SPARK_VERSION}-bin-hadoop3"

# 如果不存在，下载并解压
if [ ! -d "$SPARK_DIR" ]; then
  echo "[DOWNLOAD] Spark $SPARK_VERSION → $SPARK_ARCHIVE"

  if command -v wget &>/dev/null; then
    # wget 带进度条
    wget --show-progress "$SPARK_URL" -O "$PROJECT_ROOT/$SPARK_ARCHIVE"
  else
    # curl 带进度条
    curl -# -L "$SPARK_URL" -o "$PROJECT_ROOT/$SPARK_ARCHIVE"
  fi

  echo "[EXTRACT] $SPARK_ARCHIVE"
  tar -xf "$PROJECT_ROOT/$SPARK_ARCHIVE" -C "$PROJECT_ROOT/spark"
  rm -f "$PROJECT_ROOT/$SPARK_ARCHIVE"
else
  echo "[SKIP] Spark already at $SPARK_DIR"
fi

# 导出环境变量
export SPARK_HOME="$SPARK_DIR"
export PATH="$SPARK_HOME/bin:$PATH"

# 复制或创建 spark-env.sh
SPARK_CONF_DIR="$SPARK_HOME/conf"
SPARK_ENV="$SPARK_CONF_DIR/spark-env.sh"
TEMPLATE="$SPARK_CONF_DIR/spark-env.sh.template"

if [ ! -f "$SPARK_ENV" ]; then
  if [ -f "$TEMPLATE" ]; then
    echo "[INFO] Copy spark-env.sh.template to spark-env.sh"
    cp "$TEMPLATE" "$SPARK_ENV"
  else
    echo "[INFO] Create empty spark-env.sh"
    touch "$SPARK_ENV"
  fi
fi

# 写入 JAVA_HOME
grep -q "^export JAVA_HOME=" "$SPARK_ENV" 2>/dev/null \
  || echo "export JAVA_HOME=$JAVA_HOME" >> "$SPARK_ENV"

echo
echo "=== Spark 环境就绪 ==="
echo " JAVA_HOME=$JAVA_HOME"
echo " SPARK_HOME=$SPARK_HOME"
echo

# -----------------------------------------------------------------------------
# 3. 安装 findspark（供 Python 使用）
# -----------------------------------------------------------------------------
if ! python3 -c "import findspark" &>/dev/null; then
  echo "[INSTALL] findspark"
  pip3 install --user findspark
else
  echo "[SKIP] findspark 已安装"
fi

echo
echo "运行验证： spark-shell --version"
spark-shell --version | head -n2
