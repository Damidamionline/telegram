from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import json
import os
import csv

app = Flask(__name__)

CSV_FILE = "wingo_results.csv"
METRICS_FILE = "metrics.json"
AUTO_BETTING_FILE = os.path.join("wingo_dashboard", "betting_flag.json")


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


def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, encoding="utf-8")
            return df.tail(10).to_dict(orient="records")
        except Exception as e:
            return [{"error": f"CSV read error: {str(e)}"}]
    return []


def set_betting_flag(status: bool):
    with open(AUTO_BETTING_FILE, "w") as f:
        json.dump({"enabled": status}, f)


def get_betting_flag():
    if not os.path.exists(AUTO_BETTING_FILE):
        return False
    with open(AUTO_BETTING_FILE, "r") as f:
        return json.load(f).get("enabled", False)


@app.route("/toggle-betting", methods=["POST"])
def toggle_betting():
    data = request.get_json()
    status = data.get("enabled", False)
    set_betting_flag(status)
    return jsonify({"success": True, "enabled": status})


@app.route("/betting-status")
def betting_status():
    return jsonify({"enabled": get_betting_flag()})


@app.route("/")
def dashboard():
    try:
        with open(CSV_FILE, encoding="utf-8", errors="ignore") as f:
            reader = list(csv.DictReader(f))
            recent = reader[-10:] if len(reader) >= 10 else reader

        recent_results = []
        for row in recent:
            try:
                confidence = f"{float(row.get('confidence', 0)) * 100:.1f}%"
            except:
                confidence = "0.0%"

            recent_results.append({
                "timestamp": row.get("timestamp", "N/A"),
                "period": row.get("period", "N/A"),
                "number": row.get("number", "N/A"),
                "actual": row.get("status", "N/A"),
                "prediction": row.get("prediction", "N/A"),
                "confidence": confidence,
                "stage": row.get("stage", "N/A"),
                "result": row.get("result", "N/A"),
                "status": row["status"]
            })

        metrics = load_metrics()
        accuracy = (
            f"{(metrics['correct_predictions'] / metrics['total_predictions'] * 100):.1f}%"
            if metrics["total_predictions"] else "N/A"
        )

        return render_template(
            "dashboard.html",
            current_stage=metrics["current_stage"],
            highest_stage=metrics["highest_stage"],
            accuracy=accuracy,
            last_prediction=metrics["last_prediction"],
            last_result=metrics["last_result"],
            recent_results=recent_results
        )
    except Exception as e:
        return f"Error loading dashboard: {e}"


@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.get_json()

        # Convert timestamp string to string if it's a datetime object
        if isinstance(data.get("timestamp"), dict):
            data["timestamp"] = data["timestamp"].get(
                "__str__", str(data["timestamp"]))

        write_header = not os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "timestamp", "period", "number", "result",
                "prediction", "confidence", "status", "stage"
            ])
            if write_header:
                writer.writeheader()
            writer.writerow(data)

        return jsonify({"message": "Uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/upload-metrics", methods=["POST"])
def receive_metrics():
    data = request.json
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return jsonify({"status": "success"}), 200


@app.route("/metrics")
def metrics():
    return send_file(METRICS_FILE, mimetype="application/json")


@app.route("/api")
def api():
    return jsonify({
        "metrics": load_metrics(),
        "results": load_data()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
