import re

relative_url_pattern = re.compile(
    r"^(?!https?:\/\/|\/\/|[a-zA-Z]:\\)[^\s]+"
)

# Test cases
test_urls = [
    "/about",
    "./contact",
    "../images/logo.png",
    "profile/edit",
    "https://example.com/full-url",
    "//example.com/protocol-relative"
]

for url in test_urls:
    if relative_url_pattern.match(url):
        print(f"Relative: {url}")
    else:
        print(f"Not relative: {url}")
