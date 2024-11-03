from datetime import datetime, timezone
import psycopg2
import os

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
        CREATE TABLE IF NOT EXISTS currently_indexing (
            indexing_start_timestamp DECIMAL,
            url TEXT UNIQUE,
            requested_to_index_timestamp DECIMAL,
            PRIMARY KEY (indexing_start_timestamp, url)
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

def get_timestamp() -> float:
    return datetime.now(timezone.utc).timestamp()

def keyword_exists(keyword:str) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM keywords WHERE keyword = %s", (keyword,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result is not None

def is_website_indexed(url:str) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM latest_website_index_time WHERE url = %s", (url,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result is not None

def add_keyword_to_index_if_not_exists(keyword:str) -> None:
    if keyword_exists(keyword):
        return

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO keywords (keyword) VALUES (%s)", (keyword,))

    conn.commit()
    cur.close()
    conn.close()

def add_indexed_website(url:str, keywords:list[str]) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    if is_website_indexed(url):
        cur.execute("UPDATE latest_website_index_time SET timestamp = %s WHERE url = %s", (get_timestamp(), url))
        cur.execute("DELETE FROM webpages_by_keyword WHERE url = %s", (url,))
    else:
        cur.execute("INSERT INTO latest_website_index_time (url, timestamp) VALUES (%s, %s)", (url, get_timestamp()))

    for keyword in keywords:
        add_keyword_to_index_if_not_exists(keyword)
        cur.execute("INSERT INTO webpages_by_keyword (keyword, url) VALUES (%s, %s)", (keyword, url))

def request_website_index(url:str) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    #Exit if website is already waiting to be indexed
    cur.execute("SELECT * FROM to_index WHERE url = %s", (url,))
    if cur.fetchone():
        return

    cur.execute("INSERT INTO to_index (timestamp, url) VALUES (%s, %s)", (get_timestamp(), url))

    conn.commit()
    cur.close()
    conn.close()