import os
import re
import itertools
import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("WikiML Cooccur") \
    .getOrCreate()
sc = spark.sparkContext

# check stopwords file
stopwords_path = "stopwords.txt"
sw = set()
if os.path.exists(stopwords_path):
    sw = set(sc.textFile(stopwords_path).flatMap(lambda l: l.split()).collect())
b_sw = sc.broadcast(sw)

# word filtering function
def is_valid(word):
    if not re.fullmatch(r"[a-zA-Z]{3,}", word):
        return False
    if word.lower() in b_sw.value:
        return False
    if word.lower() in {"html", "href", "div", "span", "mw", "li", "id"}:
        return False
    return True

# extract_pairs function
def extract_pairs(rec):
    path, text = rec
    fname = os.path.basename(path)
    parts = fname.rstrip(".txt").split("_")
    year = parts[-3]

    for line in text.split("\n"):
        tokens = line.lower()
        for ch in '"!#$%&()*+,-./:;<=>?@[\\\\]^_`{|}~':
            tokens = tokens.replace(ch, " ")
        words = tokens.split()
        clean_words = [w for w in words if is_valid(w)]
        for w1, w2 in itertools.combinations(clean_words, 2):
            if w1 != w2:
                yield ((year, w1, w2), 1)

# local files
rdd = sc.wholeTextFiles("data/wikipedia-ml/*.txt")

# RDD aggregation
agg = rdd.flatMap(extract_pairs).reduceByKey(lambda a, b: a + b)

# transform to DataFrame
df = agg.map(lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[1])) \
        .toDF(["year", "word_1", "word_2", "count"])

# top10 co-occurrences of each year
for row in df.select("year").distinct().collect():
    y = row.year
    print(f"Year {y}:")
    df.filter(df.year == y) \
      .orderBy(col("count").desc()) \
      .show(10, truncate=False)

spark.stop()