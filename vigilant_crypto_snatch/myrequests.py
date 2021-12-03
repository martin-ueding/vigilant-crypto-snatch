from typing import Dict

import requests


class HttpRequestError(Exception):
    pass


def perform_http_request(url, json=None) -> Dict:
    try:
        if json:
            r = requests.post(url, json=json)
        else:
            r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        raise HttpRequestError(
            "We had a connection error, likely just a temporary glitch."
        ) from e
    except requests.exceptions.ReadTimeout as e:
        raise HttpRequestError(
            "We had a read timeout, likely just a temporary glitch."
        ) from e
    except requests.exceptions.HTTPError as e:
        raise HttpRequestError(
            "We had a general HTTP error, likely just a temporary glitch."
        ) from e

    if r.status_code != 200:
        raise HttpRequestError(
            f"The HTTP API has not returned a success: {r.status_code}"
        )
    return r.json()
