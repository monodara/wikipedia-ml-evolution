#!/usr/bin/env python3
import sys
from collections import defaultdict

# 用字典累加每个词对的计数
counts = defaultdict(int)

for line in sys.stdin:
    try:
        key, cnt = line.strip().split("\t")
        counts[key] += int(cnt)
    except ValueError:
        continue

# 按计数倒序输出
for key, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=False):
    print(f"{key}\t{cnt}")
