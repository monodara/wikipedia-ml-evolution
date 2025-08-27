import os
import re
import argparse
import findspark
findspark.init()

from pyspark.sql import SparkSession

parser = argparse.ArgumentParser()
parser.add_argument("--n", type=int, default=3, help="Length of n-gram")
args = parser.parse_args()
ngram_n = args.n

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("WikiML Ngram") \
    .getOrCreate()
sc = spark.sparkContext

# check stopwords file
stopwords_path = "stopwords.txt"
sw = set()
if os.path.exists(stopwords_path):
    sw = set(sc.textFile(stopwords_path).flatMap(lambda l: l.split()).collect())
b_sw = sc.broadcast(sw)

# clean and lower
def lower_clean_str(line):
    line = line.lower()
    for ch in '"!#$%&()*+,-./:;<=>?@[\\\\]^_`{|}~':
        line = line.replace(ch, " ")
    return line

# n-gram generation function
def generate_ngram(word_list, n):
    return [tuple(word_list[i:i+n]) for i in range(len(word_list)-n+1)]

# extract year function
def get_year(path):
    fname = os.path.basename(path)
    parts = fname.rstrip(".txt").split("_")
    return parts[-3]

# word filtering function
def is_valid(word):
    if not re.fullmatch(r"[a-zA-Z]{3,}", word):
        return False
    if word.lower() in b_sw.value:
        return False
    if word.lower() in {"html", "href", "div", "span", "mw", "li", "id"}:
        return False
    return True

# get all article paths
all_article_paths_rdd = sc.wholeTextFiles("data/wikipedia-ml/*.txt").map(lambda x: x[0])

# build year → RDD mapping
year_ngram_rdd_dict = {}
for article_path in all_article_paths_rdd.collect():
    text_rdd = sc.textFile(article_path)
    ngram_rdd = text_rdd.map(lambda line: lower_clean_str(line).split()) \
                         .map(lambda words: [w for w in words if is_valid(w)]) \
                         .flatMap(lambda word_list: generate_ngram(word_list, ngram_n)) \
                         .map(lambda ngram: (ngram, 1))
    year = get_year(article_path)
    if year not in year_ngram_rdd_dict:
        year_ngram_rdd_dict[year] = ngram_rdd
    else:
        year_ngram_rdd_dict[year] = year_ngram_rdd_dict[year].union(ngram_rdd)

# show top10 of each year
for year in year_ngram_rdd_dict:
    print(year)
    rdd = year_ngram_rdd_dict[year].reduceByKey(lambda x, y: x + y)
    df = rdd.map(lambda l: (*l[0], l[1])) \
            .toDF([f"word_{i}" for i in range(ngram_n)] + ["count"])
    df.orderBy("count", ascending=False).show(10)

spark.stop()