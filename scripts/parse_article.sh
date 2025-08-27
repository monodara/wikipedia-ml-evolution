#!/usr/bin/env bash
export LC_ALL=C
set -euo pipefail

INPUT_DIR="data/wikipedia-ml-raw"
OUTPUT_DIR="data/wikipedia-ml"
mkdir -p "$OUTPUT_DIR"

for html in "$INPUT_DIR"/machine-learning-*.html; do
  # 1) 提取标题和 footer 文本
  if command -v pup &>/dev/null; then
    full_title=$(pup 'head > title text{}' < "$html")
    footer=$(pup 'li#footer-info-lastmod text{}' < "$html")
    content=$(pup 'div#mw-content-text > div.mw-parser-output > p text{}' < "$html")
  else
    full_title=$(sed -n 's|.*<title>\(.*\)</title>.*|\1|p;q' "$html")
    footer=$(grep -m1 'This page was last edited on' "$html" || true)
    content=$(grep -o '<p>[^<]\+</p>' "$html" \
              | sed -e 's|<p>||g' -e 's|</p>||g')
  fi

  # 2) 用正则直接从 footer 捕获 day, month_name, year（更稳健，能处理 "... (UTC)."）
  if [[ $footer =~ ([0-9]{1,2})[[:space:]]+([A-Za-z]+)[[:space:]]+([0-9]{4}) ]]; then
    day=${BASH_REMATCH[1]}
    month_name=${BASH_REMATCH[2]}
    year=${BASH_REMATCH[3]}
  else
    # 回退：先去掉可能的 "(UTC)."，再拆分
    date_str=$(echo "$footer" | sed -E 's|.*last edited on ||; s|,.*||; s/\s*\(UTC\)\.?$//')
    day=${date_str%% *}
    rest=${date_str#* }
    month_name=${rest% *}
    year=${rest##* }
  fi

  # 3) 标题规范化，去掉残留的 "(UTC)" 并替换对文件名危险的字符
  page_title=${full_title// - /-}
  page_title=${page_title//"(UTC)."/}
  page_title=${page_title//"(UTC)"/}
  page_title=${page_title//\//-}
  page_title=${page_title//:/-}

  # 4) 月份英文转数字（保持你原来的映射）
  case "${month_name:0:3}" in
    Jan) month=1;; Feb) month=2;; Mar) month=3;; Apr) month=4;;
    May) month=5;; Jun) month=6;; Jul) month=7;; Aug) month=8;;
    Sep) month=9;; Oct) month=10;; Nov) month=11;; Dec) month=12;;
    *)   month=0;;
  esac

  # 5) 写文件
  outfile="$OUTPUT_DIR/article_${page_title}_${year}_${month}_${day}.txt"
  printf "%s\n" "$content" > "$outfile"
  echo "Parsed → $outfile"
done
