from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pandas as pd
from random import choice, randint
import waybackpy
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address

websitesDir = "./WebsiteList"

app = Flask(__name__)
CORS(app)
# limiter = Limiter(
#     get_remote_address,
#     app=app,
#     default_limits=["5 per minute"]
# )

# Read all csv files in the directory 
# Files 2003.csv to 2022.csv
# Ignore column 1
def readAllFiles():
    websites = {}
    for i in range(2003, 2023):
        filename = websitesDir + "/" + str(i) + ".csv"
        df = pd.read_csv(filename, header=None, usecols=[1])
        websites[str(i)] = df[1].tolist()
    return websites
        

websites = readAllFiles()

@app.route('/getAllWebsites/<year>', methods=['GET'])
def getWebsite(year):
    if year in websites:
        return jsonify(websites[year])
    else:
        return jsonify({"error": "Year not found"}), 404

def randomWebsite():
    year = randint(2003, 2022)
    return [choice(websites[str(year)]), year]

def random_day_month_time():
    month = randint(1, 12)
    day = randint(1, 30)
    hour = randint(0, 23)
    minute = randint(0, 59)
    second = randint(0, 59)
    return f"{month}{day}{hour}{minute}{second}"



@app.route('/getRandomWebsite', methods=['GET'])
# @limiter.limit("1 per 1 seconds")
def getRandomWebsite():
    website, year = randomWebsite()
    print(website, year)
    timestamp = str(year) + random_day_month_time()
    print(timestamp)
    cdx_api = waybackpy.WaybackMachineCDXServerAPI(website)
    cdx_api.closest = timestamp
    cdx_api.sort = 'closest'
    cdx_api.limit = 5
    snapshot = {}
    for item in cdx_api.snapshots():
        snapshot = item
        break
    year = snapshot.timestamp[:4]
    return jsonify({"url": snapshot.archive_url, "year": year})

def rewrite_urls(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    proxy_base = "http://localhost:5000/filter?url="
    for tag in soup.find_all("a", href=True):
        tag["href"] = proxy_base + urljoin(base_url, tag["href"])
        if tag.get("target") == "_blank":
            print(tag)
            tag["target"] = "_self"
    # Ensure <img>, <script>, and <link> sources remain absolute and resolve to the original site
    for tag in soup.find_all(["img", "script", "link"], {"src": True}):
        tag["src"] = urljoin(base_url, tag["src"])    
    return str(soup)

# Vibe coded proxy, pezi na min dulevi
@app.route('/filter', methods=['GET'])
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    try:
        response = requests.get(url)
        # response.encoding = "utf-8"
        print(response.encoding)
        encoding = response.apparent_encoding
        print(encoding)
        response.encoding = encoding
        content_type = response.headers.get("Content-Type", "")
        pattern = r"\b(200\d|201\d|202\d|199\d)\b"
        
        if response.status_code == 200:
            if "text/html" in content_type:
                modified_html = rewrite_urls(response.text, url)
                filtered_content = re.sub(pattern, "[REDACTED]", modified_html, flags=re.IGNORECASE)
                return Response(filtered_content, content_type=content_type)
            
            return Response(response.content.decode(encoding), content_type=content_type)
        else:
            return jsonify({"error": "Failed to fetch content"}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)