[![Shell](https://img.shields.io/badge/Shell-121011?style=flat&logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Hadoop Streaming](https://img.shields.io/badge/Hadoop%20Streaming-66CCFF?style=flat&logo=apache-hadoop&logoColor=white)](https://hadoop.apache.org/docs/current/hadoop-streaming/HadoopStreaming.html)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=flat&logo=apache-spark&logoColor=white)](https://spark.apache.org/)

# Wikipedia Machine Learning Article Evolution Analysis

This project analyzes the historical evolution of the Wikipedia "Machine learning" article using a combination of shell scripts, Hadoop streaming, and Apache Spark. It extracts article revisions, parses content, and computes co-occurrence and n-gram statistics over time.

---

## 📁 Project Structure

```
.
├── data                        # Contains articles about ml crawled from Wikipedia
├── hadoop
│   ├── scripts
│   │   ├── hadoop_setup.sh     # Download & install Hadoop
│   │   ├── upload_to_hdfs.sh   # Upload articles' text file to Hadoop
│   │   ├── run_bigram.sh       # Run mapper&reducer to analyse bigram
│   │   ├── run_cooccur.sh       # Run mapper&reducer to analyse co-occurrence
│   └── streaming
│   │   ├── mapper_cooccur.py
│   │   ├── reducer_cooccur.py
│   │   ├── mapper_bigram.py
│   │   ├── reducer_bigram.py
│   │   ├── combiner_bigram.py
├── README.md
├── scripts
│   ├── data_collection.py
│   ├── generate_article_ids.py # Choose 1 article in 1 month since 2020
│   ├── download.sh             # Get Wikipedia html based on article ids
│   └── parse_article.sh        # Parse raw ml html to text and clean
├── spark
│   ├── scripts
│   │   ├── spark_setup.sh      # install & configure spark
│   └── streaming
│   │   ├── map_reducer_coocur.py
│   │   ├── map_reducer_ngram.py
└── stopwords.txt
```

---

## ⚙️ Setup Instructions

1. Clone the repository and navigate to the project root.

2. Prepare data <br>    
    Generate article revision IDs:
   ```bash
   python scripts/generate_article_ids.py
   ```

    Download and parse Wikipedia articles:
   ```bash
   python scripts/data_collection.py
   ```

3. Install dependencies:
   ```bash
   pip install findspark
   ```

4. Download and extract Spark :
   ```bash
   bash spark/scripts/spark_setup.sh
   ```

5. Download and set up Hadoop:
   ```bash
   bash hadoop/scripts/hadoop_setup.sh
   ```

6. Upload article files to hdfs:
   ```bash
   bash upload_to_hdfs.sh
   ```

---

## 🚀 Analysis Scripts

### Co-occurrence Analysis (Spark)

Compute word pair co-occurrence frequencies per year:

```bash
spark-submit spark/streaming/map_reducer_coocur.py
```

### N-gram Analysis (Spark)

Compute n-gram frequencies per year (change the argument --n):

```bash
spark-submit spark/streaming/map_reducer_ngram.py --n 3
```

---

## 📌 Notes

- All parsed articles are stored in `data/wikipedia-ml/` with filenames like:
  ```
  article_Machine learning-Wikipedia_2016_7_14.txt
  ```

- Stopwords are loaded from `stopwords.txt` and broadcasted in Spark jobs.

- Both Spark scripts include robust text cleaning and filtering logic:
  - Remove punctuation, digits, HTML tags, and short or meaningless tokens.
  - Only retain alphabetic words with length ≥ 3 not in the stopword list.

---

## 📈 Output

Each analysis script prints the top 10 results per year to the console. You can modify the scripts to save results to CSV or visualize trends.
