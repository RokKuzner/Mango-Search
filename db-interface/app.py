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

def create_tables_if_not_exist() -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
                keyword TEXT UNIQUE PRIMARY KEY
        )   
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS webpages_by_keyword (
                keyword TEXT PRIMARY KEY,
                url TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS to_index (
                timestamp DECIMAL PRIMARY KEY,
                url TEXT UNIQUE NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS latest_website_index_time (
                url TEXT UNIQUE PRIMARY KEY,
                timestamp DECIMAL NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

@app.route('/data', methods=['GET'])
def get_data():
    data = [{"status": "success", "message": "THIS IS A TEST"}]
    return jsonify(data)

if __name__ == '__main__':
    #Create db tables if they do not exist
    create_tables_if_not_exist()

    app.run(host='0.0.0.0', port=5000)