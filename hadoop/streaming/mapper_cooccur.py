#!/usr/bin/env python3
import sys
import os
import string
import io
import re
import traceback

# ----------------------------------------
# support stdin ignore invalid UTF-8
# ----------------------------------------
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')

print("DEBUG: mapper started", file=sys.stderr)

# ----------------------------------------
# automatic locate stopwords.txt
# ----------------------------------------
SW = "stopwords.txt"

# load stopwords
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
# filter function: exclude URLs and words with digits
# ----------------------------------------
def is_valid_word(word: str) -> bool:
    word = word.lower()
    if not word:
        return False
    # exclude words with digits
    if any(c.isdigit() for c in word):
        return False
    # URL / domains
    if word.startswith("www.") or ".com" in word or ".org" in word or ".edu" in word:
        return False
    # too short or too long
    if len(word) < 2 or len(word) > 25:
        return False
    # at least one letter
    if not re.search(r"[a-z]", word):
        return False
    # exclude weird symbols
    if re.search(r"[\\{}\[\]=+\-*/<>|^~]", word):
        return False
    # exclude low letter ratio tokens (for example "x\approx,Uyghurche")
    letters = re.findall(r"[a-z]", word)
    if len(letters) < max(2, len(word) // 2):
        return False
    return True

# ----------------------------------------
# process standard input line by line, output word pairs
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
                        # output format: word1,word2<tab>1
                        print(f"{wi},{wj}\t1")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
