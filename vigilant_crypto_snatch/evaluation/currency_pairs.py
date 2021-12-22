from typing import List
from typing import Tuple

from ..myrequests import perform_http_request


def get_currency_pairs(api_key: str) -> list:
    response = request_currency_pairs(api_key)
    return parse_currency_pairs(response)


def request_currency_pairs(api_key: str) -> dict:
    r = perform_http_request(
        f"https://min-api.cryptocompare.com/data/v2/pair/mapping/exchange"
        f"?e=Kraken"
        f"&api_key={api_key}"
    )
    return r


def parse_currency_pairs(response: dict) -> List[Tuple[str, str]]:
    data = response["Data"]["current"]
    pairs = [(e["fsym"], e["tsym"]) for e in data]
    return pairs


def get_available_fiats(available_pairs: List[Tuple[str, str]]) -> List[str]:
    if ("BTC", "EUR") not in available_pairs:
        available_pairs.append(("BTC", "EUR"))
    available_fiats = list({f for c, f in available_pairs})
    available_fiats.sort()
    return available_fiats


def get_available_coins(available_pairs: List[Tuple[str, str]], fiat: str) -> List[str]:
    if ("BTC", "EUR") not in available_pairs:
        available_pairs.append(("BTC", "EUR"))
    available_coins = list({c for c, f in available_pairs if f == fiat})
    available_coins.sort()
    return available_coins
