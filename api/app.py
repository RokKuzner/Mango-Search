from flask import Flask, request, jsonify, make_response
import functions as db_functions
from search import search
import signal
import urllib.parse
import re
from datetime import datetime, timezone

valid_base_url_regex_pattern = re.compile(r"^(?:https?:\/\/)(?:www\.)?(?P<domain_name>[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{0,251}[a-zA-Z0-9])?)(?P<top_level_domain>\.[a-zA-Z]{2,63})(?:\/)$")

app = Flask(__name__)

@app.route("/request_website_index", methods=["POST"])
def request_website_index_endpoint():
    data = request.json
    if "url" not in data:
        return make_response(jsonify({"status": "error", "message": "Missing 'url' key in request data"}), 400)
    url = data["url"]

    # Check if the given url is valid and of a base website
    if not valid_base_url_regex_pattern.match(url):
        return make_response(jsonify({"status": "forbidden", "display_msg":"The given URL is not valid."}), 403)

    # Check if the website was indexed less than half an hour ago
    last_index_time = db_functions.get_last_index_time(url)
    curent_timestamp = db_functions.get_timestamp()

    if last_index_time and (curent_timestamp - last_index_time) < 1800:
        return make_response(jsonify({"status": "forbidden", "display_msg":"You cannot request website index of a website that was indexed less than 30 minutes ago."}), 403)

    # Run the indexing process
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

@app.route("/get_last_website_index_time", methods=["GET"])
def get_last_website_index_time_endpoint():
    data = request.json
    if "url" not in data:
        return make_response(jsonify({"status": "error", "message": "Missing 'url' key in request data"}), 400)
    url = data["url"]

    # Check if the given url is valid and of a base website
    if not valid_base_url_regex_pattern.match(url):
        return make_response(jsonify({"status": "forbidden", "display_msg":"The given URL is not valid."}), 403)
    
    index_timestamp = db_functions.get_last_index_time(url)

    if not index_timestamp:
        return make_response(jsonify({"status": "forbidden", "display_msg":"The given website was not indexed yet."}), 403)
    
    index_datetime_obj = datetime.fromtimestamp(float(index_timestamp), timezone.utc)
    index_string_time = f"{index_datetime_obj.hour}:{index_datetime_obj.minute}:{index_datetime_obj.second}, {index_datetime_obj.day}. {index_datetime_obj.month}. {index_datetime_obj.year} (DD. MM. YYYY) UTC"

    return make_response(jsonify({"status": "success", "index_time":index_string_time}), 200)

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

@app.route("/search", methods=["GET"])
def search_endpoint():
    query = urllib.parse.unquote(request.args.get("q"))

    if not query:
        return make_response(jsonify({"status":"error", "message":"missing query argument"}))
    
    return_objects = search(query)

    return make_response(jsonify({"status":"succes", "result":return_objects}), 200)

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