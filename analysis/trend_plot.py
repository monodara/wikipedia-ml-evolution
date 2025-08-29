from heatmap_utils import load_cooccur_data
import matplotlib.pyplot as plt

full_df = load_cooccur_data()
trend_df = full_df.pivot_table(index="year", columns="pair", values="count", aggfunc="sum").fillna(0)
trend_df = trend_df.sort_index()

top_pairs = trend_df.sum().sort_values(ascending=False).head(2).index.tolist()

plt.figure(figsize=(10, 6))
for pair in top_pairs:
    plt.plot(trend_df.index, trend_df[pair], marker="o", label=pair)

plt.title("Trend of Top 2 Word Pairs Over Time")
plt.xlabel("Year")
plt.ylabel("Frequency")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("artifacts/visuals/cooccur_trends.png")
plt.show()