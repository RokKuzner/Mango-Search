from crawler import MangoCrawler

import requests
import threading
import time
import signal

class WorkerHandler():
    def __init__(self):
        self.DB_INTERFACE_URL = 'http://api:5000'
        self.MAX_WORKERS = 5
        self.WORKERS = []

        self.work = True

    def start_next_website_index_process(self) -> str:
        response = requests.get(f'{self.DB_INTERFACE_URL}/start_next_website_index_process')
        if response.status_code != 200:
            return None
        return response.json()['url']
    
    def run(self):
        while self.work:
            #Give workers jobs
            while len(self.WORKERS) < self.MAX_WORKERS:
                url = self.start_next_website_index_process()
                if url is None:
                    break

                worker = MangoCrawler()
                worker_thread = threading.Thread(target=worker.crawl_website, args=(url,))
                worker_thread.start()

                self.WORKERS.append(worker)

                print(f"Crawler starting job at {url}")

            #Delete finished workers
            filtered_workers = []
            for worker in self.WORKERS:
                if worker.is_active:
                    filtered_workers.append(worker)
            self.WORKERS = filtered_workers
            filtered_workers.clear()

            time.sleep(1)

    def stop(self):
        self.work = False

if __name__ == "__main__":
    handler = WorkerHandler()

    #Set up interrupt signals
    signal.signal(signal.SIGTERM, handler.stop)
    signal.signal(signal.SIGINT, handler.stop)

    handler.run()