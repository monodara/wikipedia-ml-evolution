#!/usr/bin/env python
# coding: utf-8

import os

# Create folder
os.makedirs("wikipedia-ml-raw", exist_ok=True)

# Run shell scripts
os.system("bash scripts/main.sh data/article-ids.txt")
os.system("bash scripts/parse_article.sh")