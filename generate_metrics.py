import pandas as pd
import json
import os

# Correct path (same folder as the script)
CSV_FILE = "wingo_results.csv"
METRICS_FILE = "metrics.json"


def generate_metrics():
    if not os.path.exists(CSV_FILE):
        print("❌ CSV file not found at", CSV_FILE)
        return

    df = pd.read_csv(CSV_FILE)

    if df.empty:
        print("❌ CSV file is empty.")
        return

    try:
        total_predictions = len(df)
        correct_predictions = len(df[df["status"] == "✅ Win"])
        highest_stage = df["stage"].max()
        current_stage = df.iloc[-1]["stage"]
        last_prediction = df.iloc[-1]["prediction"]
        last_confidence = float(df.iloc[-1]["confidence"])
        last_result = df.iloc[-1]["result"]
        last_timestamp = df.iloc[-1]["timestamp"]
        last_outcome = df.iloc[-1]["status"]

        metrics = {
            "current_stage": int(current_stage),
            "highest_stage": int(highest_stage),
            "correct_predictions": int(correct_predictions),
            "total_predictions": int(total_predictions),
            "last_prediction": str(last_prediction),
            "last_confidence": float(last_confidence),
            "last_result": str(last_result),
            "last_timestamp": str(last_timestamp),
            "last_outcome": str(last_outcome)
        }

        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        print("✅ metrics.json saved successfully.")

    except Exception as e:
        print(f"❌ Failed to save metrics.json: {e}")


if __name__ == "__main__":
    generate_metrics()
