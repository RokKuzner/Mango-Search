from flask import Flask, request, jsonify, make_response
import functions as db_functions
import signal

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

@app.route("/list_websites_to_index", methods=["GET"])
def get_websites_to_index_list_endpoint():
    return make_response(jsonify({"status":"succes", "data":db_functions.list_websites_to_index()}))

@app.route("/check_website_in_index_quee", methods=["POST"])
def check_website_in_index_quee_endpoint():
    post_data = request.json
    if "url" not in post_data:
        return make_response(jsonify({"status":"error", "message":"url not present in json data"}))
    
    try:
        result = db_functions.is_website_in_index_quee(post_data["url"])
    except Exception as e:
        return make_response(jsonify({"status": "error"}), 500)

    return make_response(jsonify({"status":"success", "data":result}), 200)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == "__main__":
    #Create db tables if they do not exist
    db_functions.create_tables_if_not_exist()

    #Set up interrupt signals
    signal.signal(signal.SIGTERM, shutdown_server)
    signal.signal(signal.SIGINT, shutdown_server)

    app.run(host='0.0.0.0', port=5000)