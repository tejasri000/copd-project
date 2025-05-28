from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Load Excel safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of backend.py
DATA_PATH = os.path.join(BASE_DIR, "prs_data.xlsx")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Required data file '{DATA_PATH}' not found.")

df = pd.read_excel(DATA_PATH)

@app.route("/search")
def search_gene():
    gene_name = request.args.get("gene", "").upper()

    if not gene_name:
        return jsonify({"error": "No gene name provided"}), 400

    gene_data = df[df["Gene Name"].str.upper() == gene_name]

    if gene_data.empty:
        return jsonify({"error": "Gene not found"}), 404

    return jsonify(gene_data.to_dict(orient="records"))

@app.route("/prs_distribution")
def prs_distribution():
    gene_name = request.args.get("gene", "").upper()

    if not gene_name:
        return jsonify({"error": "No gene name provided"}), 400

    gene_data = df[df["Gene Name"].str.upper() == gene_name]

    if gene_data.empty:
        return jsonify({"Low": 0, "Medium": 0, "High": 0})

    prs_score = gene_data["Effect Size (Beta)"].sum()

    if prs_score < 0.5:
        return jsonify({"Low": prs_score, "Medium": 0, "High": 0})
    elif prs_score < 1.0:
        return jsonify({"Low": 0, "Medium": prs_score, "High": 0})
    else:
        return jsonify({"Low": 0, "Medium": 0, "High": prs_score})

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(debug=True)
