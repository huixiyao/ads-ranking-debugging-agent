import numpy as np
import pandas as pd


route_scale = {
    "MAIN": 1.05, # Main Route has impression guardrail 
    "SUP1": 1.2, # Supplementary route 1 has higher privilege
    "SUP2": 1.1,  # Supplementary route 2 tends to be high-value / high-score
    "SUP3": 1.0    # Supplementary route 3 tends to be weaker but valuable for cold-start
}

def add_simulated_fields(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    在 Avazu 数据上添加模拟 Ads Ranking 相关字段：
    - surface: 模拟 FEED / REELS / STORY
    - route_id: 模拟 MAIN / FR / PRM / CUFR
    - rank_score: 模拟排序分（与 click 略相关）
    - pred_ctr: 模拟模型预测 ctr（真实 ctr + 噪声）
    """
    rng = np.random.default_rng(seed)

    # 模拟 surface（展示页面）
    surfaces = ["S1", "S2", "S3"]
    df["surface"] = rng.choice(surfaces, size=len(df), p=[0.4, 0.4, 0.2])

    # 模拟 route（检索路由）
    routes = ["MAIN", "SUP1", "SUP2", "SUP3"]
    # 简单设一个大概的配比
    df["route_id"] = rng.choice(routes, size=len(df), p=[0.5, 0.2, 0.2, 0.1])

    # 模拟 pred_ctr：真实 ctr + 高斯噪声，截断在 [0, 1]
    noise = rng.normal(loc=0.0, scale=0.05, size=len(df))
    df["pred_ctr"] = np.clip(df["ctr"] + noise, 0.0, 1.0)

    # 模拟 rank_score：基础分 + 若有点击略加一点
    df["rank_score"] = df.apply(
        lambda row: row["pred_ctr"] * route_scale[row["route_id"]] + np.random.normal(0, 0.02),
        axis=1
    )


    return df
