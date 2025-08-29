import pandas as pd
import os

def load_cooccur_data(data_dir="artifacts/cooccur_top10"):
    dfs = []
    for file in os.listdir(data_dir):
        if file.endswith(".csv"):
            year = file.split("_")[-1].split(".")[0]
            df = pd.read_csv(os.path.join(data_dir, file))
            df["year"] = year
            df["pair"] = df["word_1"] + " + " + df["word_2"]
            dfs.append(df)
    return pd.concat(dfs)