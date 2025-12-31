import json
from src.agent import run

def main():
    out = run("metrics_sample.json")

    with open("debug_report.json", "w") as f:
        json.dump(out["report"], f, indent=2)

    with open("debug_report.md", "w") as f:
        f.write(out["report_markdown"])

    print("Wrote debug_report.json and debug_report.md")

if __name__ == "__main__":
    main()
