import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Load all yearly top10 CSVs
data_dir = "artifacts/cooccur_top10"
dfs = []

for file in os.listdir(data_dir):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(data_dir, file))
        df["pair"] = df["word_1"] + " + " + df["word_2"]
        dfs.append(df)

full_df = pd.concat(dfs)

# Aggregate total frequency per word pair
pair_freq = full_df.groupby("pair")["count"].sum().sort_values(ascending=False)

# Select top N pairs
top_n = 20
top_pairs = pair_freq.head(top_n)

# Prepare data for heatmap
heatmap_data = np.array(top_pairs.values).reshape(-1, 1)

# Plot heatmap
plt.figure(figsize=(6, 10))
plt.imshow(heatmap_data, cmap="YlGnBu", aspect="auto")
plt.yticks(ticks=np.arange(top_n), labels=top_pairs.index)
plt.xticks([0], ["Total Frequency"])
plt.colorbar(label="Frequency")
plt.title("Top Word Pair Co-occurrence (All Years Combined)")
os.makedirs("artifacts/visuals", exist_ok=True)
plt.tight_layout()
plt.savefig("artifacts/visuals/cooccur_heatmap_overall.png")
plt.show()
plt.close()