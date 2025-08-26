#!/bin/bash
# 将 HTML 文件提取成纯文本，输出到 data/wikipedia-ml/*.txt

IN_DIR="data/wikipedia-ml-raw"
OUT_DIR="data/wikipedia-ml"
mkdir -p "$OUT_DIR"

for file in "$IN_DIR"/*.html; do
  base=$(basename "$file" .html)
  # 使用 lynx 提取正文，也可换成 html2text、pup 等工具
  lynx -dump -nolist "$file" > "$OUT_DIR/${base}.txt"
  echo "Parsed $file -> ${base}.txt"
done
