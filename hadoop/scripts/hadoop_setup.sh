#!/usr/bin/env bash
set -e

##############################################################################
# 1. 基本变量
##############################################################################
HADOOP_VERSION=3.3.3
INSTALL_DIR=/usr/local/hadoop-${HADOOP_VERSION}
TARBALL=hadoop-${HADOOP_VERSION}.tar.gz

# 下载源
PRIMARY_URL=https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/${TARBALL}
ARCHIVE_URL=https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/${TARBALL}
MIRROR_URL=https://mirrors.huaweicloud.com/apache/hadoop/common/hadoop-${HADOOP_VERSION}/${TARBALL}

# 端口
NN_RPC_PORT=9000
NN_HTTP_PORT=9870
RM_HTTP_PORT=8088

# 本地 HDFS 存储
HDFS_DATA=$HOME/hadoop-data

echo "=== Hadoop Setup v${HADOOP_VERSION} ==="

##############################################################################
# 2. 安装检测：存在即跳过下载／解压
##############################################################################
if [ -d "${INSTALL_DIR}" ]; then
  echo "[SKIP] Hadoop already installed at ${INSTALL_DIR}"
else
  echo "=== Download & install Hadoop ${HADOOP_VERSION} ==="
  set +e
  if command -v wget >/dev/null 2>&1; then
    wget "${PRIMARY_URL}"; RET=$?
  else
    curl -L "${PRIMARY_URL}" -o "${TARBALL}"; RET=$?
  fi
  if [ $RET -ne 0 ] || [ ! -f "${TARBALL}" ]; then
    wget "${ARCHIVE_URL}" || curl -L "${ARCHIVE_URL}" -o "${TARBALL}"
  fi
  if [ ! -f "${TARBALL}" ]; then
    wget "${MIRROR_URL}" || curl -L "${MIRROR_URL}" -o "${TARBALL}"
  fi
  set -e

  [ -f "${TARBALL}" ] || { echo "ERROR: download failed"; exit 1; }
  tar -xzf "${TARBALL}"

  # 删除旧目录，避免嵌套
  [ -d "${INSTALL_DIR}" ] && sudo rm -rf "${INSTALL_DIR}"
  sudo mv "hadoop-${HADOOP_VERSION}" "${INSTALL_DIR}"
  rm -f "${TARBALL}"
  echo "Hadoop installed under ${INSTALL_DIR}"
fi

##############################################################################
# 3. 环境变量 + Java 11 检测
##############################################################################
JAVA_11_FOUND=false

# macOS Homebrew 安装路径
if [ -d "/usr/local/opt/openjdk@11" ]; then
  export JAVA_HOME=/usr/local/opt/openjdk@11
  JAVA_11_FOUND=true
elif [ -d "/opt/homebrew/opt/openjdk@11" ]; then
  # Apple Silicon (M1/M2/M3)
  export JAVA_HOME=/opt/homebrew/opt/openjdk@11
  JAVA_11_FOUND=true
# Linux 常见路径
elif [ -d "/usr/lib/jvm/java-11-openjdk-amd64" ]; then
  export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
  JAVA_11_FOUND=true
fi

if [ "$JAVA_11_FOUND" = false ]; then
  echo "ERROR: Java 11 not found. Hadoop 3.3.3 requires Java 11."
  echo "Please install OpenJDK 11:"
  echo "  macOS (Homebrew): brew install openjdk@11"
  echo "  Ubuntu/Debian: sudo apt install openjdk-11-jdk"
  exit 1
fi

# 设置 Hadoop 路径
export HADOOP_HOME=${INSTALL_DIR}
export PATH=${JAVA_HOME}/bin:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${PATH}

# 显示使用的 Java 版本
JAVA_VER=$($JAVA_HOME/bin/java -version 2>&1 | awk -F\" '/version/ {print $2}')
echo "[INFO] Hadoop will run with Java $JAVA_VER at $JAVA_HOME"


##############################################################################
# 4. 停止本地守护进程 & 清理 PID
##############################################################################
echo "Stopping existing daemons (local mode)…"
hdfs --daemon stop namenode        || true
hdfs --daemon stop datanode        || true
hdfs --daemon stop secondarynamenode || true
yarn --daemon stop resourcemanager   || true
yarn --daemon stop nodemanager      || true

echo "Cleaning old PID files…"
for role in namenode datanode secondarynamenode resourcemanager nodemanager; do
  rm -f "/tmp/hadoop-${USER}-${role}.pid"
done

##############################################################################
# 5. 准备日志 & HDFS 目录
##############################################################################
mkdir -p ${HADOOP_HOME}/logs

echo "Preparing HDFS data under ${HDFS_DATA}…"
mkdir -p "${HDFS_DATA}/name" "${HDFS_DATA}/data"
chmod -R 755 "${HDFS_DATA}"

##############################################################################
# 6. 生成 core-site.xml、hdfs-site.xml、yarn-site.xml
##############################################################################
cat > ${HADOOP_HOME}/etc/hadoop/core-site.xml <<EOF
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://localhost:${NN_RPC_PORT}</value>
  </property>
</configuration>
EOF

cat > ${HADOOP_HOME}/etc/hadoop/hdfs-site.xml <<EOF
<configuration>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file://${HDFS_DATA}/name</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file://${HDFS_DATA}/data</value>
  </property>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
</configuration>
EOF

cat > ${HADOOP_HOME}/etc/hadoop/yarn-site.xml <<EOF
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>localhost</value>
  </property>
</configuration>
EOF

##############################################################################
# 7. 条件格式化 NameNode（首次运行时执行）
##############################################################################
if [ ! -d "${HDFS_DATA}/name/current" ]; then
  echo "Formatting HDFS NameNode (non-interactive)…"
  hdfs namenode -format -force -nonInteractive
else
  echo "[SKIP] NameNode already formatted"
fi

##############################################################################
# 8. 启动本地模式 HDFS & YARN
##############################################################################
echo "Starting HDFS daemons locally…"
hdfs --daemon start namenode
hdfs --daemon start datanode
hdfs --daemon start secondarynamenode

echo "Starting YARN daemons locally…"
yarn --daemon start resourcemanager
yarn --daemon start nodemanager

##############################################################################
# 9. 验证进程 & 打印 UI 地址
##############################################################################
echo
echo "---- Current Hadoop Java Processes ----"
jps
echo
echo "NameNode web UI → http://localhost:${NN_HTTP_PORT}"
echo "YARN   web UI → http://localhost:${RM_HTTP_PORT}"
