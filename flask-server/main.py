from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from random import choice, randint
import waybackpy
from urllib.parse import urljoin, urlparse
import threading
import queue
import Proxy
from time import sleep

websitesDir = "~/Documents/React/NetGuessr/flask-server/WebsiteList"
N = 10
app = Flask(__name__)
CORS(app)

def readAllFiles():
    websites = {}
    for i in range(2003, 2023):
        filename = websitesDir + "/" + str(i) + ".csv"
        df = pd.read_csv(filename, header=None, usecols=[1])
        websites[str(i)] = df[1].tolist()
    return websites

websites = readAllFiles()

def randomWebsite():
    year = randint(2003, 2022)
    return [choice(websites[str(year)]), year]

def randomDayMonthTime():
    month = randint(1, 12)
    day = randint(1, 30)
    hour = randint(0, 23)
    minute = randint(0, 59)
    second = randint(0, 59)
    return f"{month:02}{day:02}{hour:02}{minute:02}{second:02}"

def randomSnapshot():
    website, year = randomWebsite()
    print(website, year)
    timestamp = str(year) + randomDayMonthTime()
    print(timestamp)
    try:
        cdx_api = waybackpy.WaybackMachineCDXServerAPI(website)
        cdx_api.closest = timestamp
        cdx_api.sort = 'closest'
        cdx_api.limit = 5
        for item in cdx_api.snapshots():
            return {"url": item.archive_url, "year": item.timestamp[:4]}
    except Exception as e:
        print(f"Error fetching snapshot: {e}")
        return {"url": None, "year": None}

url_queue = queue.Queue(maxsize=N)
worker_thread = None  # To track the worker thread

def fetchAndAddToQueue():
    try:
        url, year = randomSnapshot().values()
        response = Proxy.fetch(url)
        if response.status_code == 200:
            url_queue.put({"response": response, "year": year}, timeout=5)
            print(f"Fetched and added to queue: {url}")
            sleep(2) # Don't spam the server
        else:
            print(f"Failed to fetch: {url}")
    except queue.Full:
        print("Queue is full, skipping fetch.")
    except Exception as e:
        print(f"Error fetching URL: {e}")

def prefetch_worker():
    while True:
        try:
            if url_queue.qsize() < N:
                print("Queue size:", url_queue.qsize())
                fetchAndAddToQueue()
            else:
                sleep(1)  # Sleep for a bit before checking again
        except Exception as e:
            print(f"Error in prefetch worker: {e}")

def start_worker_thread():
    global worker_thread
    if worker_thread is None or not worker_thread.is_alive():
        worker_thread = threading.Thread(target=prefetch_worker, daemon=True)
        # print thread id
        print(f"Thread ID: {worker_thread.ident}")
        worker_thread.start()
        print("Prefetch worker thread started.")
    else:
        print("Prefetch worker thread is already running.")

@app.route('/generatePage', methods=['GET'])
def generatePage():
    if not url_queue.empty():
        url = url_queue.get()
        print(f"Serving pre: {url}")
        return url["response"]
    else:
        url = randomSnapshot()
        print(f"Serving random: {url}")
        response = Proxy.fetch(url["url"])
        if response.status_code == 200:
            return response
        else:
            return jsonify({"error": "Failed to fetch URL"}), 500

@app.route('/filter', methods=['GET'])
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    return Proxy.fetch(url)

if __name__ == '__main__':
    start_worker_thread()  # Ensure the worker thread starts only once
    app.run(debug=True, use_reloader=False)