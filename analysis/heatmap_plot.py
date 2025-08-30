from heatmap_utils import load_cooccur_data
import matplotlib.pyplot as plt
import numpy as np
import os

# ---------------- 参数 ----------------
TOP_N = 30
OUTPUT_DIR = "artifacts/visuals"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- 数据加载与聚合 ----------------
full_df = load_cooccur_data()
pair_freq = (
    full_df.groupby("pair")["count"]
    .sum()
    .sort_values(ascending=False)
)
top_pairs = pair_freq.head(TOP_N)

# ---------------- 热力图数据 ----------------
heatmap_data = np.array(top_pairs.values).reshape(-1, 1)
labels = top_pairs.index.tolist()

# ---------------- 绘制 ----------------
fig, ax = plt.subplots(figsize=(6, max(6, len(labels) * 0.4)))

c = ax.pcolormesh(
    heatmap_data,
    cmap="YlGnBu",
    edgecolors="k",
    linewidths=0.2
)

# 颜色条（保持高度一致）
cbar = fig.colorbar(c, ax=ax, aspect=30)
cbar.set_label("Frequency")

# 轴标签
ax.set_title(f"Top {TOP_N} Word Pair Co-occurrence (All Years Combined)")
ax.set_xticks([0.5])
ax.set_xticklabels(["Total Frequency"])
ax.set_yticks(np.arange(len(labels)) + 0.5)
ax.set_yticklabels(labels)

# 倒序 y 轴：高频在上
ax.invert_yaxis()

# 在格子中加数值（可选）
for i, value in enumerate(heatmap_data.flatten()):
    ax.text(
        0.5, i + 0.5, str(value),
        ha="center", va="center",
        fontsize=8, color="black"
    )

# 布局 & 保存
plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, f"cooccur_heatmap_total_top{TOP_N}.png")
plt.savefig(output_path, dpi=300)
plt.show()
plt.close()
