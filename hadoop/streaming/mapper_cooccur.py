#!/usr/bin/env python3
import sys
import os
import string
import io
import re
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
            w = w.strip().lower()
            if w:
                stopwords_list.append(w)
    print(f"DEBUG: stopwords loaded, total={len(stopwords_list)}", file=sys.stderr)
except Exception as e:
    print(f"ERROR: failed to load stopwords.txt: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# ----------------------------------------
# 过滤函数：排除网址、数字、乱码、公式类 token
# ----------------------------------------
def is_valid_word(word: str) -> bool:
    word = word.lower()
    if not word:
        return False
    # 含数字直接排除
    if any(c.isdigit() for c in word):
        return False
    # URL / 域名
    if word.startswith("www.") or ".com" in word or ".org" in word or ".edu" in word:
        return False
    # 长度过短或过长
    if len(word) < 2 or len(word) > 25:
        return False
    # 至少要包含一个字母
    if not re.search(r"[a-z]", word):
        return False
    # 排除有奇怪符号的 token
    if re.search(r"[\\{}\[\]=+\-*/<>|^~]", word):
        return False
    # 字母比例太低的垃圾 token（比如 "x\approx,Uyghurche"）
    letters = re.findall(r"[a-z]", word)
    if len(letters) < max(2, len(word) // 2):
        return False
    return True

# ----------------------------------------
# 逐行处理标准输入，输出词对
# ----------------------------------------
for line in sys.stdin:
    try:
        line = line.strip()
        if not line:
            continue
        words = line.split()
        n = len(words)
        for i in range(n):
            for j in range(i+1, n):
                wi = words[i].strip(string.punctuation.replace("'", ""))
                wj = words[j].strip(string.punctuation.replace("'", ""))
                li, lj = wi.lower(), wj.lower()
                if li and lj and li not in stopwords_list and lj not in stopwords_list:
                    if is_valid_word(li) and is_valid_word(lj):
                        # 输出格式：word1,word2<tab>1
                        print(f"{wi},{wj}\t1")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
