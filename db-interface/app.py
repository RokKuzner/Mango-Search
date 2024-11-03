from flask import Flask, request, jsonify
from function import *

app = Flask(__name__)

@app.route('/data', methods=['GET'])
def get_data():
    data = [{"status": "success", "message": "THIS IS A TEST"}]
    return jsonify(data)

if __name__ == '__main__':
    #Create db tables if they do not exist
    create_tables_if_not_exist()

    app.run(host='0.0.0.0', port=5000)