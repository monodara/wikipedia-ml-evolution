from heatmap_utils import load_cooccur_data
import matplotlib.pyplot as plt
import numpy as np
import os

# 创建输出目录
os.makedirs("artifacts/visuals", exist_ok=True)

# 加载数据
full_df = load_cooccur_data()

# 聚合所有年份的总频率
pair_freq = full_df.groupby("pair")["count"].sum().sort_values(ascending=False)

# 选取前 N 个高频词对
top_n = 30
top_pairs = pair_freq.head(top_n)

# 准备热力图数据
heatmap_data = np.array(top_pairs.values).reshape(-1, 1)
labels = top_pairs.index.tolist()

# 绘制热力图（单列）
plt.figure(figsize=(6, max(6, len(labels) * 0.4)))
plt.imshow(heatmap_data, cmap="YlGnBu", aspect="auto", vmin=0, vmax=heatmap_data.max())

plt.yticks(ticks=np.arange(len(labels)), labels=labels)
plt.xticks([0], ["Total Frequency"])
plt.colorbar(label="Frequency")
plt.title("Top Word Pair Co-occurrence (All Years Combined)")
plt.tight_layout()
plt.savefig("artifacts/visuals/cooccur_heatmap_total.png")
plt.show()
plt.close()