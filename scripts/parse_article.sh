#!/bin/bash
# extract text from HTML files
# install lynx tool

IN_DIR="data/wikipedia-ml-raw"
OUT_DIR="data/wikipedia-ml"
mkdir -p "$OUT_DIR"

for file in "$IN_DIR"/*.html; do
  base=$(basename "$file" .html)
  # use lynx to extract text, can also use html2text, pup, etc.
  lynx -dump -nolist "$file" > "$OUT_DIR/${base}.txt"
  echo "Parsed $file -> ${base}.txt"
done
