import pandas as pd

def compute_basic_metrics(df: pd.DataFrame) -> dict:
    """
    Compute core metrics for Ads Ranking debugging.
    """
    metrics = {}

    # 1. Global CTR
    global_ctr = df["click"].mean()
    metrics["global_ctr"] = float(global_ctr)

    # 2. Route-level metrics
    route_group = df.groupby("route_id").agg(
        ctr=("click", "mean"),
        impressions=("impr", "sum"),
        avg_pred_ctr=("pred_ctr", "mean"),
        avg_rank_score=("rank_score", "mean"),
    )

    total_impr = route_group["impressions"].sum()
    route_group["share"] = route_group["impressions"] / total_impr
    route_group["efficiency"] = route_group["ctr"] / global_ctr

    metrics["route_stats"] = route_group.round(4).to_dict(orient="index")

    # 3. Surface-level metrics
    surface_group = df.groupby("surface").agg(
        ctr=("click", "mean"),
        impressions=("impr", "sum"),
    )
    surface_group["share"] = surface_group["impressions"] / surface_group["impressions"].sum()

    metrics["surface_stats"] = surface_group.round(4).to_dict(orient="index")

    # 4. Calibration drift
    metrics["calibration_drift"] = float((df["pred_ctr"] - df["ctr"]).mean())

    return metrics
