#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime, timedelta
from mwclient import Site
import time
import sys

# 配置区
TITLE    = "Machine learning"
OUTFILE  = "data/article-ids.txt"
STEP_DAYS = 30
RETRIES   = 3
BACKOFF   = 5  # 初始退避秒数

def fetch_revision_ids(page, start_dt, end_dt):
    """
    在 [start_dt, end_dt) 区间内，获取最新的一次修订 revid
    """
    for attempt in range(RETRIES):
        try:
            # prop="ids" 仅获取 revid，limit=1 最早的一条
            revs = list(page.revisions(start=start_dt, end=end_dt,
                                       dir="newer", prop="ids", limit=1))
            return revs[0]["revid"] if revs else None
        except Exception as e:
            wait = BACKOFF * (attempt + 1)
            print(f"[WARN] 第 {attempt+1} 次尝试失败，{wait}s 后重试… ({e})")
            time.sleep(wait)
    print(f"[ERROR] 区间 {start_dt}–{end_dt} 多次重试仍失败，跳过。", file=sys.stderr)
    return None

def main():
    site = Site("en.wikipedia.org")              # 默认为 HTTPS 和标准 UA
    page = site.pages[TITLE]

    start_date = datetime(2010, 1, 1)
    end_date   = datetime.utcnow()
    step       = timedelta(days=STEP_DAYS)

    revision_ids = []

    current = start_date
    while current < end_date:
        next_dt = current + step

        rvstart = current.strftime("%Y-%m-%dT%H:%M:%SZ")
        rvend   = next_dt.strftime(   "%Y-%m-%dT%H:%M:%SZ")

        revid = fetch_revision_ids(page, rvstart, rvend)
        if revid:
            revision_ids.append(str(revid))

        current = next_dt

    # 写入文件
    with open(OUTFILE, "w", encoding="utf-8") as f:
        for rid in revision_ids:
            f.write(rid + "\n")

    print(f"已保存 {len(revision_ids)} 个修订 ID 到 {OUTFILE}")

if __name__ == "__main__":
    main()
