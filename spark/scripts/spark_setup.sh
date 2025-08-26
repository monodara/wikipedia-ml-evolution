!apt-get install openjdk-8-jdk-headless -qq > /dev/null
!wget https://archive.apache.org/dist/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz
!tar xf spark-3.3.1-bin-hadoop3.tgz
!rm spark-3.3.1-bin-hadoop3.tgz   # Tidying up
# Setting up environmental variables: 
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.3.1-bin-hadoop3"

# install the findpark library to locate Spark
!pip install -q findspark
import findspark
findspark.init()

# import SparkSession from pyspark.sql to create entry point to Spark.
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").getOrCreate()
spark.conf.set("spark.sql.repl.eagerEval.enabled", True)

# Create SparkContext:
sc = spark.sparkContext