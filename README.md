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
│   ├── generate_article_ids.py
│   ├── download.sh
│   └── parse_article.sh
├── spark
│   ├── scripts
│   └── streaming
└── stopwords.txt
```

---

## ⚙️ Setup Instructions

1. Clone the repository and navigate to the project root.

2. Install dependencies:
   ```bash
   pip install findspark
   ```

3. Download and extract Spark (already included under `spark/`):
   ```bash
   bash scripts/setup_spark.py
   ```

4. Generate article revision IDs:
   ```bash
   python scripts/generate_article_ids.py
   ```

5. Download and parse Wikipedia articles:
   ```bash
   python scripts/data_collection.py
   ```

---

## 🚀 Analysis Scripts

### Co-occurrence Analysis (Spark)

Compute word pair co-occurrence frequencies per year:

```bash
spark-submit spark/streaming/map_reducer_coocur.py
```

### N-gram Analysis (Spark)

Compute n-gram frequencies per year (default n=3):

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
