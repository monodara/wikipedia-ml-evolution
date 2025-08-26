#!/usr/bin/env python3
import sys
import os
import string
import io
import traceback

# ----------------------------------------
# support stdin ignore invalid UTF-8
# ----------------------------------------
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')

print("DEBUG: mapper started", file=sys.stderr)

# ----------------------------------------
# automatically locate stopwords.txt file   
# ----------------------------------------
SW = "stopwords.txt"

# load stopwords
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
# filter function: exclude URLs and words with digits
# ----------------------------------------
def is_valid_word(word):
    word = word.lower()
    if any(c.isdigit() for c in word):
        return False
    if word.startswith("www.") or ".com" in word or ".org" in word or ".edu" in word:
        return False
    return True

# remove punctuation except apostrophe
translator = str.maketrans("", "", string.punctuation.replace("'", ""))

# process standard input line by line, output bigrams
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
