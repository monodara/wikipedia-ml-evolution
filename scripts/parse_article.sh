#!/usr/bin/env bash
set -euo pipefail

# 1. 输入/输出目录
INPUT_DIR="data/wikipedia-ml-raw"
OUTPUT_DIR="data/wikipedia-ml"
mkdir -p "$OUTPUT_DIR"

# 2. 遍历所有抓下来的 HTML 文件
for html in "$INPUT_DIR"/machine-learning-*.html; do
  # 原始文件名（不带后缀）
  base=$(basename "$html" .html)

  # 提取 <title>Machine learning - Wikipedia</title> 中的 “Machine learning”
  title=$(grep -oP '(?<=<title>).*?(?= - Wikipedia)' "$html" | head -1)
  # 空格改下划线
  title=${title// /_}

  # 提取 “This page was last edited on 1 January 2020”
  date_str=$(grep -oP 'This page was last edited on \K[0-9]{1,2} [A-Za-z]+ [0-9]{4}' "$html" | head -1)
  day=$(echo "$date_str" | awk '{print $1}')
  month_name=$(echo "$date_str" | awk '{print $2}')
  year=$(echo "$date_str" | awk '{print $3}')

  # 月份名称转数字
  case "$month_name" in
    January)   month=1  ;;
    February)  month=2  ;;
    March)     month=3  ;;
    April)     month=4  ;;
    May)       month=5  ;;
    June)      month=6  ;;
    July)      month=7  ;;
    August)    month=8  ;;
    September) month=9  ;;
    October)   month=10 ;;
    November)  month=11 ;;
    December)  month=12 ;;
    *)          month=0  ;;
  esac

  # 输出文件名格式：article_Title_年_月_日.txt
  outfile="$OUTPUT_DIR/article_${title}_${year}_${month}_${day}.txt"

  # 只抓正文部分：优先 pup，否则用 lynx+sed
  if command -v pup &>/dev/null; then
    pup 'div#mw-content-text .mw-parser-output p text{}' < "$html" > "$outfile"
  else
    lynx -dump -nolist -force_html "$html" \
      | sed -n '/^Contents$/,/^References$/p' \
      | sed '1d;$d' \
      > "$outfile"
  fi

  echo "Parsed → $outfile"
done
