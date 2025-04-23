import logging
import json
import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
from collections import Counter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# endpoints
URL_HAUS_ENDPOINT = "https://urlhaus.abuse.ch/downloads/text/"
LOCAL_ENDPOINT = "localhost"
LOCAL_PORT = 80

# local paths
ALLOW_LIST_PATH = "/allowlist"
DENY_LIST_PATH = "/denylist"

# create a global requests session
SESSION = requests.Session()
RETRIES = Retry(total=5, backoff_factor=0.5)
SESSION.mount("https://", HTTPAdapter(max_retries=RETRIES))
SESSION.mount("http://", HTTPAdapter(max_retries=RETRIES))


# hit the api get the current list of urls from the urlhaus
def _parse_urls_to_json(urls):
    try:
        logging.info("Parsing URL list to JSON")
        urls = urls.split("\n")
        urls_list = []
        for url in urls:
            if url.startswith("#") or url == "":
                continue
            else:
                urls_list.append(url.replace("\r", ""))
        return urls_list
    except Exception as e:
        logging.error(f"Error parsing URL list to JSON: {e}")
        return []


def get_url_list():
    try:
        logging.info("Fetching URL list")
        response = SESSION.get(URL_HAUS_ENDPOINT)
        response.raise_for_status()
        urls = _parse_urls_to_json(response.text)
        return urls
    except RequestException as e:
        logging.error(f"Error fetching URL list: {e}")
        return []


current_url_list = get_url_list()
logging.info(f"Current URL list len: {len(current_url_list)}")

# run the tests against the local server

# get 1000 random urls from the current list
random_urls = random.sample(current_url_list, 1000)

# add the random urls to the allow list
response = SESSION.post(
    f"http://{LOCAL_ENDPOINT}:{LOCAL_PORT}{ALLOW_LIST_PATH}", json=random_urls
)
assert response.status_code == 201, f"Allow list POST status code is ({response.status_code}), expexted 201"
assert (
    sorted(response.json().get("urls_added", [])) == sorted(random_urls)
), "Allow list data is not correct"

# check the allow list api to make sure that the data was added
response = SESSION.get(f"http://{LOCAL_ENDPOINT}:{LOCAL_PORT}{ALLOW_LIST_PATH}")
assert response.status_code == 200, "Allow list GET status code is not 200"
assert sorted(response.json()) == sorted(random_urls), "The allow list data is not correct"

# check the allow list to make sure there are no duplicates - hit the post api 30 times and add random items to the allow list
hit_count = 0
for i in range(0, 15):
    random_urls = random.sample(current_url_list, 5)
    # hit the api two times to add the items two times for sure
    for j in range(0, 2):
        logging.info(f"Hit count: {hit_count}")
        response = SESSION.post(
            f"http://{LOCAL_ENDPOINT}:{LOCAL_PORT}{ALLOW_LIST_PATH}", json=random_urls
        )
        assert response.status_code == 201, "Allow list POST status code is not 201"
        assert (
            response.json().get("message", "") == "URLs added to the allowlist"
        ), "Allow list message is not correct"
        assert (
            sorted(response.json().get("urls_added", [])) == sorted(random_urls)
        ), "Allow list data is not correct"
        hit_count += 1

# get the allow list and check the counts
response = SESSION.get(f"http://{LOCAL_ENDPOINT}:{LOCAL_PORT}{ALLOW_LIST_PATH}")
assert response.status_code == 200, "Allow list GET status code is not 200"
url_counts = Counter(response.json())
for url, count in url_counts.items():
    assert count == 1, f"URL: {url} is in the allow list {count} times"

# check to make sure that the items added to the allow list are not in the deny list
# get the allow list
response = SESSION.get(f"http://{LOCAL_ENDPOINT}:{LOCAL_PORT}{ALLOW_LIST_PATH}")
assert response.status_code == 200, "Allow list GET status code is not 200"
allow_list = response.json()
# get the deny list
response = SESSION.get(f"http://{LOCAL_ENDPOINT}:{LOCAL_PORT}{DENY_LIST_PATH}")
assert response.status_code == 200, "Deny list GET status code is not 200"
deny_list = response.json()
deny_set = set(deny_list)
assert (
    isinstance(deny_list, list)
), "Deny list is not a list type in the response json"
# check the allow list against the deny list
for url in allow_list:
    assert url not in deny_set, f"URL: {url} is in the deny list"
