from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        port=os.getenv('DATABASE_PORT')
    )
    return conn

@app.route('/data', methods=['GET'])
def get_data():
    data = [{"status": "success", "message": "THIS IS A TEST"}]
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)