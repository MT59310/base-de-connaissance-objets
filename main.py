from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Service actif"}), 200

@app.route("/process", methods=["POST"])
def process():
    data = request.json
    return jsonify({"status": "received", "size": len(str(data))})
