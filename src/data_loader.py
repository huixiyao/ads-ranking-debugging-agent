import pandas as pd

def load_sample_csv(path="/data/train.csv", nrows=100000):
    """
    加载 Avazu train.csv 的一个子集，避免一次性读太大。
    每一行视为一次展示，click=1 表示有点击。
    """
    df = pd.read_csv(path, nrows=nrows)
    # Avazu 有一列叫 'click'，0 或 1
    # 我们先简单定义：每行都是一次展示
    df["impr"] = 1
    df["ctr"] = df["click"]  # 0/1，后面可以用 mean(ctr) 当整体 CTR
    return df