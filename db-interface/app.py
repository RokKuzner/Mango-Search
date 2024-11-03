from flask import Flask, request, jsonify, make_response
import functions as db_functions

app = Flask(__name__)

@app.route("/request_website_index", methods=["POST"])
def request_website_index_endpoint():
    data = request.json
    if "url" not in data:
        return make_response(jsonify({"status": "error", "message": "Missing 'url' key in request data"}), 400)
    url = data["url"]

    try:
        db_functions.request_website_index(url)
    except Exception as e:
        return make_response(jsonify({"status": "error"}), 500)

    return make_response(jsonify({"status": "success"}), 200)

@app.route("/start_next_website_index_process", methods=["GET"])
def start_next_website_index_endpoint():
    try:
        url = db_functions.start_next_website_index_process()
    except Exception as e:
        return make_response(jsonify({"status": "error"}), 500)

    return make_response(jsonify({"url": url}), 200)

@app.route("/add_indexed_website", methods=["POST"])
def add_indexed_website_endpoint():
    data = request.json
    if "url" not in data or "keywords" not in data:
        return make_response(jsonify({"status": "error", "message": "Missing 'url' or 'keywords' key in request data"}), 400)
    url = data["url"]
    keywords = data["keywords"]

    try:
        db_functions.add_indexed_website(url, keywords)
    except Exception as e:
        return make_response(jsonify({"status": "error"}), 500)

    return make_response(jsonify({"status": "success"}), 200)

if __name__ == "__main__":
    #Create db tables if they do not exist
    db_functions.create_tables_if_not_exist()

    app.run(host='0.0.0.0', port=5000)