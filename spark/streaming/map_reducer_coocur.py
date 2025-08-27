import os
import findspark
findspark.init()      # 自动找到 SPARK_HOME

from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .master("local[*]") \
    .appName("WikiML") \
    .getOrCreate()
# Create SparkContext:
sc = spark.sparkContext

# Read stopwords
stopwords = sc.textFile("stopwords.txt").flatMap(lambda line: line.split()).collect()
# Define a function to filter refs
def is_article(title):
  return "article" in title
# Read all files in the folder "wikipedia-ml"
all_file_rdd = sc.wholeTextFiles("wikipedia-ml")
# Remove refs
all_article_rdd = all_file_rdd.filter(lambda x: is_article(x[0]))
# Get all articles' paths
all_article_paths_rdd = all_article_rdd.map(lambda x: x[0])
print(all_article_paths_rdd.collect())

year_rdd_dict = {}

# Define a method to get the years of the articles
def get_year(title):
  date_info = title.split("-")[2]
  year = date_info.split("_")[1]
  return year

# Extract every year when there's articles collected
all_year = all_article_rdd.map(lambda x: get_year(x[0])).distinct()

# Define a function for removing punctuations
def lower_clean_str(x):
  punc='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'
  lowercased_str = x.lower()
  for ch in punc:
    lowercased_str = lowercased_str.replace(ch, '')
  return lowercased_str

# Define a function for filtering stopwords
def not_stopwords(word):
  return not(word in stopwords)
import itertools
for article_path in all_article_paths_rdd.collect():
  # Read one article as an RDD:
  text_rdd = sc.textFile(article_path)
  # compute the co-occurrence RDD
  co_occur_rdd = text_rdd.map(lambda line: lower_clean_str(line).split()) \
                  .flatMap(lambda word: itertools.combinations(word, 2)) \
                  .filter(lambda comb: not_stopwords(comb[0]) and not_stopwords(comb[1])) \
                  .filter(lambda comb: comb[0] != comb[1]) \
                  .filter(lambda comb: len(comb[0]) > 1 and len(comb[1]) > 1) \
                  .map(lambda comb: (comb, 1))
                  
  # Store RDDs to the dictionary {year, RDD-union}
  article_year = get_year(article_path)
  if(not(article_year in year_rdd_dict)):
    year_rdd_dict[article_year] = co_occur_rdd
  else:
    unioned_rdd = year_rdd_dict[article_year].union(co_occur_rdd)
    year_rdd_dict[article_year] = unioned_rdd

# create dataframe for each year and compute top ten co-occurances
for year in year_rdd_dict:
  print(year)
  rdd = year_rdd_dict[year].reduceByKey(lambda x, y: x + y)
  # Create dataframe
  columns = ["word_0", "word_1", "count"]
  df = rdd.map(lambda l: (l[0][0],l[0][1],l[1])).toDF(columns)
  df.orderBy("count",ascending=False).show(10)