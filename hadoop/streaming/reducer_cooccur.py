#!/usr/bin/env python3
import sys
from collections import defaultdict

# Use dictionary to accumulate counts for each word pair
counts = defaultdict(int)

for line in sys.stdin:
    try:
        key, cnt = line.strip().split("\t")
        counts[key] += int(cnt)
    except ValueError:
        continue

# output results in descending order by count
for key, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=False):
    print(f"{key}\t{cnt}")
