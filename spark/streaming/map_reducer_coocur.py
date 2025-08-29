import os
import re
import itertools
import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

import pandas as pd

# Initialize Spark
spark = SparkSession.builder \
    .master("local[*]") \
    .appName("WikiML Cooccur") \
    .getOrCreate()
sc = spark.sparkContext

# Load stopwords
stopwords_path = "stopwords.txt"
sw = set()
if os.path.exists(stopwords_path):
    sw = set(sc.textFile(stopwords_path).flatMap(lambda l: l.split()).collect())
b_sw = sc.broadcast(sw)

# Word filtering function
def is_valid(word):
    word = word.lower()
    if not re.fullmatch(r"[a-zA-Z]{3,}", word):
        return False
    if word in b_sw.value:
        return False
    if word in {"html", "href", "div", "span", "mw", "li", "id", "hlist", "ref", "cite", "template"}:
        return False
    if word.startswith("wiki") or word.startswith("cat") or word.endswith("list"):
        return False
    return True


# Extract word pairs from each article
def extract_pairs(rec):
    path, text = rec
    fname = os.path.basename(path)
    parts = fname.rstrip(".txt").split("_")
    year = parts[-3]

    for line in text.split("\n"):
        tokens = line.lower()
        for ch in '"!#$%&()*+,-./:;<=>?@[\\]^_`{|}~':
            tokens = tokens.replace(ch, " ")
        words = tokens.split()
        clean_words = [w for w in words if is_valid(w)]
        for w1, w2 in itertools.combinations(clean_words, 2):
            if w1 != w2:
                yield ((year, w1, w2), 1)

# Load article files
rdd = sc.wholeTextFiles("data/wikipedia-ml/*.txt")

# Aggregate word pair counts
agg = rdd.flatMap(extract_pairs).reduceByKey(lambda a, b: a + b)

# Convert to DataFrame
df = agg.map(lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[1])) \
        .toDF(["year", "word_1", "word_2", "count"])

# Save top 10 co-occurrences per year as individual CSV files
output_dir = "artifacts/cooccur_top10"
os.makedirs(output_dir, exist_ok=True)

for row in df.select("year").distinct().collect():
    y = row.year
    top10 = df.filter(df.year == y) \
              .orderBy(col("count").desc()) \
              .limit(10)
    pdf = top10.toPandas()
    pdf.to_csv(f"{output_dir}/cooccur_top10_{y}.csv", index=False)

spark.stop()
