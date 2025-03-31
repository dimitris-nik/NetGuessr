from flask import Response, jsonify
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def redactYears(html_content):
    def replaceYear(match):
        year = match.group(0)
        before, after = match.span()
        # Check if the match is inside an HTML tag
        if re.search(r'<[^>]*$', html_content[:before]) and re.search(r'^[^>]*>', html_content[after:]):
            return year  # Don't replace if inside an HTML tag
        return '[REDACTED]'
    return re.sub(r'(?<!\d)(19[9][1-9]|20\d{2}|2100)(?!\d)', replaceYear, html_content)

def extractArchiveUrl(url: str) -> str:
    """Returns the domain and the first two path segments from a given URL."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path.strip("/")  # Remove leading/trailing slashes
    segments = path.split("/")[:2]  # Get the first two segments
    new_path = "/" + "/".join(segments) if segments else ""
    return f"{parsed_url.scheme}://{domain}{new_path}"

def fixUrls(html, base_url, proxy_url="http://localhost:5000/filter?url="):
    soup = BeautifulSoup(html, "html.parser")
    # Ensure hrefs are absolute and redirect to the proxy
    # for tag in soup.find_all(["a", "link"], {"href": True}):
        # CSS links don't need to be proxied
        # if tag.name == "link" and tag.get("type") == "text/css":
        #     continue
        # tag["href"] = proxy_url + urljoin(base_url, tag["href"])
    for tag in soup.find_all(["a", "link", "script"], {"href": True}):
        tag["href"] = proxy_url + urljoin(base_url, tag["href"])
    archive_url = extractArchiveUrl(base_url)
    # Ensure relativbe web.archive.org URLs redirect to the proxy
    for tag in soup.find_all(["img", "script", "link", "audio", "video", "source", "iframe"], {"src": True}):
        destination = tag["src"]
        match = re.search('''(?:(?:https?:)?//web.archive.org)?/web/([^/]+/)(.+)''', destination)
        if match:
            tag["src"] = archive_url + "/" +  match.group(2)
        else:
            tag["src"] = base_url + urlparse(destination).path[1:]
        print(tag["src"])
    return str(soup)

def fetch(url):
    try:
        print("Fetching", url)
        r = requests.get(url)
        print("Fetched", url)
        if not r.apparent_encoding:
            r.encoding = "utf-8"
        else:
            r.encoding = r.apparent_encoding
        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "")
            if "text/html" in content_type:
                modified_html = fixUrls(r.content.decode(r.encoding), url)
                redacted_html = redactYears(modified_html)
                return Response(redacted_html)
            else:
                return Response(r.content, content_type=content_type)
        else:
            return Response(jsonify({"error": f"Failed to fetch URL: {r.status_code}"}), status=r.status_code)
    except requests.exceptions.RequestException as e:
        return Response(jsonify({"error": "Request failed"}), status=500)
