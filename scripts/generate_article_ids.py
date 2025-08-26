#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime, timedelta
from mwclient import Site
import time
import sys

# Configuration
TITLE    = "Machine learning"
OUTFILE  = "data/article-ids.txt"
STEP_DAYS = 30
RETRIES   = 3
BACKOFF   = 5  # Initial backoff in seconds

def fetch_revision_ids(page, start_dt, end_dt):
    """
    in the [start_dt, end_dt) range, get the latest revision revid
    """
    for attempt in range(RETRIES):
        try:
            # prop="ids" Only get the revid, limit=1 for the earliest one
            revs = list(page.revisions(start=start_dt, end=end_dt,
                                       dir="newer", prop="ids", limit=1))
            return revs[0]["revid"] if revs else None
        except Exception as e:
            wait = BACKOFF * (attempt + 1)
            print(f"[WARN]  {attempt+1} times failed, retrying in {wait}s… ({e})")
            time.sleep(wait)
    print(f"[ERROR] Failed to retrieve revisions in range {start_dt}–{end_dt} after multiple attempts, skipping.", file=sys.stderr)
    return None

def main():
    site = Site("en.wikipedia.org")              # Default to HTTPS and standard UA
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

    # Write to file
    with open(OUTFILE, "w", encoding="utf-8") as f:
        for rid in revision_ids:
            f.write(rid + "\n")

    print(f"Saved {len(revision_ids)} revision IDs to {OUTFILE}")

if __name__ == "__main__":
    main()
