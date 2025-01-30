from datetime import datetime, timezone
import psycopg2
import os
from typing import Optional
import time
import urllib.parse

def get_db_connection():
    # !! WARNING !!
    # #YOU MUST SET THESE UP IN THE .env FILE
    # WICH IS INCLUDED IN THE .dockerignore FOR SAFETY REASONS
    # !! WARNING !!
    db_connection_params = {
        "host":os.getenv('POSTGRES_HOST'),
        "dbname":os.getenv('POSTGRES_DB'),
        "user":os.getenv('POSTGRES_USER'),
        "password":os.getenv('POSTGRES_PASSWORD'),
        "port":os.getenv('POSTGRES_PORT')
    }
    
    attempts = 0
    conn = None
    while attempts < 5:
        try:
            conn = psycopg2.connect(**db_connection_params)
            break
        except psycopg2.OperationalError:
            attempts += 1
        
        time.sleep(1)

    if conn is None:
        raise Exception("Failed to connect to the database after 5 attempts.")

    return conn

def create_tables_if_not_exist() -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    cur.execute("SET pg_trgm.similarity_threshold = 0.5;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
                keyword TEXT UNIQUE PRIMARY KEY
        )   
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS keywords_trgm_idx ON keywords USING gin (keyword gin_trgm_ops);")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS webpages_by_keyword (
                keyword TEXT,
                url TEXT,
                PRIMARY KEY (keyword, url)
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

def clean_strip_url(url:str) -> str:
    """Cleans and strips a url. Example: "https://www.google.com/search?q=lol" -> "https://www.google.com/"
    
    Keyword arguments:
    url -- the url to clean and strip
    Return: stripped and cleaned url
    """

    parsed_url = urllib.parse.urlparse(url)
    clean_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", "")) + "/"

    return clean_url

# Database related funtions   
def keyword_exists(keyword:str) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM keywords WHERE keyword = %s", (keyword,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result is not None

def is_website_indexed(url:str) -> bool:
    url = clean_strip_url(url)

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
    url = clean_strip_url(url)

    conn = get_db_connection()
    cur = conn.cursor()

    #Remove website from currently_indexing table
    cur.execute("DELETE FROM currently_indexing WHERE url = %s", (url,))

    if is_website_indexed(url):
        cur.execute("UPDATE latest_website_index_time SET timestamp = %s WHERE url = %s", (get_timestamp(), url))
        cur.execute("DELETE FROM webpages_by_keyword WHERE url = %s", (url,))
    else:
        cur.execute("INSERT INTO latest_website_index_time (url, timestamp) VALUES (%s, %s)", (url, get_timestamp()))

    for keyword in keywords:
        add_keyword_to_index_if_not_exists(keyword)
        cur.execute("INSERT INTO webpages_by_keyword (keyword, url) VALUES (%s, %s)", (keyword, url))

    conn.commit()
    cur.close()
    conn.close()

def request_website_index(url:str) -> None:
    url = clean_strip_url(url)

    conn = get_db_connection()
    cur = conn.cursor()

    #Exit if website is already waiting to be indexed
    cur.execute("SELECT * FROM to_index WHERE url = %s", (url,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return

    cur.execute("INSERT INTO to_index (timestamp, url) VALUES (%s, %s)", (get_timestamp(), url))

    conn.commit()
    cur.close()
    conn.close()

def start_next_website_index_process() -> Optional[str]:
    """
    Starts the indexing process for the next website in the queue.

    This function selects the oldest website from the 'to_index' table,
    removes it from the table, and adds it to the 'currently_indexing' table
    with the current timestamp. If no websites are in the queue, it returns None.

    Returns:
        str | None: The URL of the website to be indexed, or None if no websites are in the queue.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM to_index ORDER BY timestamp ASC LIMIT 1")
    result = cur.fetchone()

    if not result:
        cur.close()
        conn.close()
        return None
    
    timestamp, url = result

    #Remove website from to_index table
    cur.execute("DELETE FROM to_index WHERE url = %s", (url,))
    #Add website to currently_indexing table
    cur.execute("INSERT INTO currently_indexing (indexing_start_timestamp, url, requested_to_index_timestamp) VALUES (%s, %s, %s)", (get_timestamp(), url, timestamp))
    
    conn.commit()
    cur.close()
    conn.close()

    return url

def get_last_index_time(url:str) -> Optional[float]:
    url = clean_strip_url(url)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT timestamp FROM latest_website_index_time WHERE url = %s", (url,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else None

def get_website_keywords(url:str) -> list[str]:
    url = clean_strip_url(url)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT keyword FROM webpages_by_keyword WHERE url = %s", (url,))
    result = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in result]

def get_websites_by_literal_keyword(keyword:str) -> list[str]:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT url FROM webpages_by_keyword WHERE keyword = %s", (keyword,))
    result = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in result]

def get_websites_by_similar_keywords(keyword:str, treshold:float=0.4):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT url, keyword, similarity(keyword, %s) AS similarity_score
        FROM webpages_by_keyword
        WHERE similarity(keyword, %s) >= %s;
    """, (keyword, keyword, treshold))
    result = cur.fetchall()

    cur.close()
    conn.close()

    return [{"url":row[0], "keyword":row[1], "similarity":row[2]} for row in result]

def list_websites_to_index() -> list[str]:
    conn = get_db_connection()
    curr = conn.cursor()

    curr.execute("SELECT url FROM to_index")
    result = curr.fetchall()

    curr.close()
    conn.close()

    return [row[0] for row in result]

def is_website_in_index_quee(url:str) -> bool:
    url = clean_strip_url(url)
    
    conn = get_db_connection()
    curr = conn.cursor()

    curr.execute("SELECT url FROM to_index WHERE url = %s", (url,))
    result = curr.fetchone()

    curr.close()
    conn.close()

    return result is not None