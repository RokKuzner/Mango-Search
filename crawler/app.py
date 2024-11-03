from crawler import MangoCrawler

import requests
import threading
import time

DB_INTERFACE_URL = 'http://db-interface:5000'
MAX_WORKERS = 5
WORKERS = []

def start_next_website_index_process() -> str:
    response = requests.get(f'{DB_INTERFACE_URL}/start_next_website_index_process')
    if response.status_code != 200:
        return None
    return response.json()['url']

while True:
    #Give workers jobs
    while len(WORKERS) < MAX_WORKERS:
        url = start_next_website_index_process()
        if url is None:
            break

        worker = MangoCrawler()
        worker_thread = threading.Thread(target=worker.crawl_website, args=(url,))
        worker_thread.start()

        WORKERS.append(worker)

    #Delete finished workers
    for worker in WORKERS:
        if worker.is_active == False:
            WORKERS.remove(worker)

    time.sleep(1)