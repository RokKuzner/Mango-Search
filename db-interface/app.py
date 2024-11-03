from flask import Flask, request, jsonify
from functions import *

app = Flask(__name__)

@app.route("/request_website_index", methods=["POST"])
def get_data():
    data = request.json
    if "url" not in data:
        return jsonify({"status": "error", "message": "Missing 'url' key in request data"}), 400
    url = data["url"]

    try:
        request_website_index(url)
    except Exception as e:
        return jsonify({"status": "error"})

    return jsonify({"status": "success"})

if __name__ == "__main__":
    #Create db tables if they do not exist
    create_tables_if_not_exist()

    app.run(host='0.0.0.0', port=5000)