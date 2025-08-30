from heatmap_utils import load_cooccur_data
import matplotlib.pyplot as plt
import numpy as np
import os

# ---------------- arguments ----------------
TOP_N = 30
OUTPUT_DIR = "artifacts/visuals"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- data loading and aggregation ----------------
full_df = load_cooccur_data()
pair_freq = (
    full_df.groupby("pair")["count"]
    .sum()
    .sort_values(ascending=False)
)
top_pairs = pair_freq.head(TOP_N)

# ---------------- heatmap data ----------------
heatmap_data = np.array(top_pairs.values).reshape(-1, 1)
labels = top_pairs.index.tolist()

# ---------------- plotting ----------------
fig, ax = plt.subplots(figsize=(6, max(6, len(labels) * 0.4)))

c = ax.pcolormesh(
    heatmap_data,
    cmap="YlGnBu",
    edgecolors="k",
    linewidths=0.2
)

# Colorbar (consistent height)
cbar = fig.colorbar(c, ax=ax, aspect=30)
cbar.set_label("Frequency")

# Axes labels
ax.set_title(f"Top {TOP_N} Word Pair Co-occurrence (All Years Combined)")
ax.set_xticks([0.5])
ax.set_xticklabels(["Total Frequency"])
ax.set_yticks(np.arange(len(labels)) + 0.5)
ax.set_yticklabels(labels)

# Invert y-axis: high frequency on top
ax.invert_yaxis()

# Add values to the cells (optional)
for i, value in enumerate(heatmap_data.flatten()):
    ax.text(
        0.5, i + 0.5, str(value),
        ha="center", va="center",
        fontsize=8, color="black"
    )

# Layout & Save
plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, f"cooccur_heatmap_total_top{TOP_N}.png")
plt.savefig(output_path, dpi=300)
plt.show()
plt.close()
