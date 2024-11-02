from typing import Any

import requests
from flask import current_app as app

from npmvisual.commonpackages import get_popular_package_names

# I will set this up soon. Need some way to test it. I can probably just call a fake
# server and log the errors.
# # Setup retry strategy in case they dislike the spam of requests
# retry_strategy = Retry(
#   total=3,  # Total number of retries
#   status_forcelist=[429, 500, 502, 503, 504],  # Status codes to retry for
#   allowed_methods=["GET", "POST"],  # HTTP methods to retry
#   backoff_factor=1  # Backoff time between retries
# )
#
# adapter = HTTPAdapter(max_retries=retry_strategy)
# http = requests.Session()
# # Mount the adapter to the session for all HTTP and HTTPS requests
# http.mount("https://", adapter)
# http.mount("http://", adapter)


def scrape_package_json(package_name) -> Any:
    # print(f"scraping package named {name}")
    url = f"https://registry.npmjs.org/{package_name}"
    app.logger.info(f"scraping package.json from {url}")

    try:
        response = requests.get(url)
        # Raise an exception for HTTP error codes
        response.raise_for_status()  # request raise for status
        r_dict = response.json()
        return r_dict
    except requests.exceptions.HTTPError as e:
        app.logger.error(e)
        print(f"HTTP error: {e}")
        if e.response.status_code == 401:
            print("Authentication required.")
        elif e.response.status_code == 403:
            print("Access denied.")
        elif e.response.status_code == 404:
            print("Resource not found.")
        elif e.response.status_code == 429:
            print("Too Many Requests.")
        elif e.response.status_code == 500:
            print("Server error.")

    except requests.exceptions.ConnectionError:
        print("Connection error.")
    except requests.exceptions.Timeout:
        print("Request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
