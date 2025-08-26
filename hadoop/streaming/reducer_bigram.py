#!/usr/bin/env python3
import sys

current_key = None
current_count = 0

for line in sys.stdin:
    key, cnt = line.strip().split("\t")
    try:
        cnt = int(cnt)
    except ValueError:
        continue

    if key == current_key:
        current_count += cnt
    else:
        if current_key:
            print(f"{current_key}\t{current_count}")
        current_key = key
        current_count = cnt

if current_key:
    print(f"{current_key}\t{current_count}")
