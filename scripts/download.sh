#!/bin/bash
input="$1"

# assure the target directory exists
mkdir -p data/wikipedia-ml-raw

while IFS= read -r id
do
  link="https://en.wikipedia.org/w/index.php?title=Machine_learning&oldid=$id"
  downloadname="index.php?title=Machine_learning&oldid=$id.html"
  filename="data/wikipedia-ml-raw/machine-learning-$id.html"
  echo "$filename"
  # Directly specify the output path, do not generate temporary files in the root directory
  wget --header="User-Agent: wikipedia-ml-evolution/1.0 (https://github.com/yourusername/wikipedia-ml-evolution)" \
       -O "$filename" -E "$link"
  sleep 0.5
done < "$input"
