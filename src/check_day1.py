from data_loader import load_sample_csv

def main():
    df = load_sample_csv("../data/train.csv", nrows=50000)
    print("Loaded rows:", len(df))
    print("Columns:", df.columns.tolist())
    print("\nHead:")
    print(df.head())

    # 简单 sanity check：整体 CTR
    global_ctr = df["click"].mean()
    print(f"\nGlobal CTR (sample): {global_ctr:.4f}")

if __name__ == "__main__":
    main()