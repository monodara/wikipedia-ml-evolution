#!/bin/bash
input="$1"

# 确保目标目录存在
mkdir -p data/wikipedia-ml-raw

while IFS= read -r id
do
  link="https://en.wikipedia.org/w/index.php?title=Machine_learning&oldid=$id"
  downloadname="index.php?title=Machine_learning&oldid=$id.html"
  filename="data/wikipedia-ml-raw/machine-learning-$id.html"
  echo "$filename"
  # 直接指定输出路径，不在根目录生成临时文件
  wget --header="User-Agent: wikipedia-ml-evolution/1.0 (https://github.com/yourusername/wikipedia-ml-evolution)" \
       -O "$filename" -E "$link"
  # 如果一定要先下再改名，也要用完整路径：
  # wget ... -E "$link" && mv "$downloadname" "$filename"
  sleep 0.5
done < "$input"
