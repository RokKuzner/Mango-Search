from flask import Flask, request, jsonify
import functions as db_functions

app = Flask(__name__)

@app.route("/request_website_index", methods=["POST"])
def request_website_index_endpoint():
    data = request.json
    if "url" not in data:
        return jsonify({"status": "error", "message": "Missing 'url' key in request data"}), 400
    url = data["url"]

    try:
        db_functions.request_website_index(url)
    except Exception as e:
        return jsonify({"status": "error"})

    return jsonify({"status": "success"})

@app.route("/start_next_website_index", methods=["GET"])
def start_next_website_index_endpoint():
    try:
        url = db_functions.start_next_website_index()
    except Exception as e:
        return jsonify({"status": "error"})

    return jsonify({"url": url})

if __name__ == "__main__":
    #Create db tables if they do not exist
    db_functions.create_tables_if_not_exist()

    app.run(host='0.0.0.0', port=5000)