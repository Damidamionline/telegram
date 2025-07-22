from flask import Flask, render_template, jsonify
import pandas as pd
import json
import os
import csv


app = Flask(__name__)

CSV_FILE = "wingo_results.csv"
METRICS_FILE = "metrics.json"


def load_metrics():
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "current_stage": 1,
            "highest_stage": 1,
            "correct_predictions": 0,
            "total_predictions": 0,
            "last_prediction": "N/A",
            "last_confidence": 0.0,
            "last_result": "N/A",
            "last_timestamp": "N/A",
            "last_outcome": "N/A"
        }


def get_current_stage():
    return load_metrics().get("current_stage", 1)


def get_highest_stage():
    return load_metrics().get("highest_stage", 1)


def get_accuracy():
    metrics = load_metrics()
    total = metrics.get("total_predictions", 0)
    correct = metrics.get("correct_predictions", 0)
    return f"{(correct / total) * 100:.1f}%" if total > 0 else "N/A"


def get_last_prediction():
    return load_metrics().get("last_prediction", "N/A")


def get_last_result():
    return load_metrics().get("last_result", "N/A")


def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, encoding="utf-8")
            return df.tail(10).to_dict(orient="records")
        except Exception as e:
            return [{"error": f"CSV read error: {str(e)}"}]
    return []


@app.route("/")
def dashboard():
    try:
        with open("wingo_results.csv", encoding="utf-8", errors="ignore") as f:
            reader = list(csv.DictReader(f))
            recent = reader[-10:] if len(reader) >= 10 else reader

        recent_results = []
        for row in recent:
            recent_results.append({
                "timestamp": row["timestamp"],
                "period": row["period"],
                "number": row["number"],
                "result": row["result"],
                "prediction": row["prediction"],
                "confidence": f"{float(row['confidence']) * 100:.1f}%",
                "status": row["status"],
                "stage": row["stage"]
            })

        metrics = load_metrics()

        return render_template(
            "dashboard.html",
            current_stage=metrics["current_stage"],
            highest_stage=metrics["highest_stage"],
            accuracy=(
                f"{(metrics['correct_predictions'] / metrics['total_predictions'] * 100):.1f}%"
                if metrics["total_predictions"] else "N/A"
            ),
            last_prediction=metrics["last_prediction"],
            last_result=metrics["last_result"],
            recent_results=recent_results
        )
    except Exception as e:
        return f"Error loading dashboard: {e}"


@app.route("/api")
def api():
    return jsonify({
        "metrics": load_metrics(),
        "results": load_data()
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
