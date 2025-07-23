import pandas as pd
import json
import os
import requests


BASE_DIR = os.path.dirname(__file__)
CSV_FILE = os.path.join(BASE_DIR, "wingo_results.csv")
METRICS_FILE = os.path.join(BASE_DIR, "metrics.json")


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
        accuracy = (correct_predictions / total_predictions) * 100

        highest_stage = int(df["stage"].max())
        current_stage = int(df.iloc[-1]["stage"])
        last_prediction = str(df.iloc[-1]["prediction"])
        last_confidence = float(df.iloc[-1]["confidence"])
        last_result = str(df.iloc[-1]["result"])
        last_timestamp = str(df.iloc[-1]["timestamp"])
        last_outcome = str(df.iloc[-1]["status"])

        metrics = {
            "current_stage": current_stage,
            "highest_stage": highest_stage,
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions,
            "last_prediction": last_prediction,
            "last_confidence": last_confidence,
            "last_result": last_result,
            "last_timestamp": last_timestamp,
            "last_outcome": last_outcome,
            "accuracy": round(accuracy, 1)
        }

        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        print("✅ metrics.json saved successfully.")

    except Exception as e:
        print(f"❌ Failed to save metrics.json: {e}")
        
    



if __name__ == "__main__":
    generate_metrics()
