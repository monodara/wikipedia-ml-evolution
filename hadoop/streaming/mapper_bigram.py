#!/usr/bin/env python3
import sys
import os
import string
import io
import traceback

# ----------------------------------------
# 支持 stdin 忽略非法 UTF-8 字符
# ----------------------------------------
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')

print("DEBUG: mapper started", file=sys.stderr)

# ----------------------------------------
# 自动定位 stopwords.txt（Hadoop Streaming 会把文件放在当前目录）
# ----------------------------------------
SW = "stopwords.txt"

# 读入停用词
stopwords_list = []
try:
    with open(SW, "r", encoding="utf-8", errors="ignore") as f:
        for w in f:
            stopwords_list.append(w.strip().lower())
    print(f"DEBUG: stopwords loaded, total={len(stopwords_list)}", file=sys.stderr)
except Exception as e:
    print(f"ERROR: failed to load stopwords.txt: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# ----------------------------------------
# 过滤函数：排除网址和含数字的词
# ----------------------------------------
def is_valid_word(word):
    word = word.lower()
    if any(c.isdigit() for c in word):
        return False
    if word.startswith("www.") or ".com" in word or ".org" in word or ".edu" in word:
        return False
    return True

# 去除标点符号
translator = str.maketrans("", "", string.punctuation.replace("'", ""))

# 逐行处理标准输入，输出 bigram
for line in sys.stdin:
    try:
        line = line.strip()
        if not line:
            continue
        words = [w.translate(translator) for w in line.split()]
        for i in range(len(words) - 1):
            w1, w2 = words[i].lower(), words[i+1].lower()
            if w1 and w2 and w1 not in stopwords_list and w2 not in stopwords_list:
                if is_valid_word(w1) and is_valid_word(w2):
                    print(f"{w1},{w2}\t1")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
