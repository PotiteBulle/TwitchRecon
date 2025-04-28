from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUSPECTS_FILE = os.path.join(BASE_DIR, "..", "suspects", "suspects.json")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/suspects")
def api_suspects():
    if os.path.exists(SUSPECTS_FILE):
        with open(SUSPECTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) # Change host 