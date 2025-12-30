import json

from data_loader import load_sample_csv
from prepare_data import add_simulated_fields
from metrics import compute_basic_metrics


def main():
    """
    Entry point for Day 2:
    Load data -> simulate ranking signals -> compute metrics.
    """

    # 1. Load a sample of training data
    df = load_sample_csv("../data/train.csv", nrows=50000)

    # 2. Add simulated ranking-related fields
    df = add_simulated_fields(df)

    # 3. Compute core debugging metrics
    metrics = compute_basic_metrics(df)

    # 4. Print metrics (for quick inspection)
    print(json.dumps(metrics, indent=2))

    # 5. Persist metrics for downstream agent consumption (Day 3)
    with open("../metrics_sample.json", "w") as f:
        json.dump(metrics, f, indent=2)


if __name__ == "__main__":
    main()
