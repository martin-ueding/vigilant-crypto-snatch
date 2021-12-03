import datetime
import json
import os
from typing import List

from .. import logger
from ..myrequests import perform_http_request


def get_hourly_data(coin: str, fiat: str, api_key: str) -> List[dict]:
    cache_file = f"~/.cache/vigilant-crypto-snatch/hourly_{coin}_{fiat}.js"
    cache_file = os.path.expanduser(cache_file)
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    if os.path.exists(cache_file):
        logger.info("Cached historic data exists.")
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
        if mtime > datetime.datetime.now() - datetime.timedelta(days=1):
            logger.info("Cached historic data is recent. Loading that.")
            with open(cache_file) as f:
                return json.load(f)

    logger.info("Requesting historic data from Crypto Compare.")
    timestamp = int(datetime.datetime.now().timestamp())
    url = (
        f"https://min-api.cryptocompare.com/data/histohour"
        f"?api_key={api_key}"
        f"&fsym={coin}&tsym={fiat}"
        f"&limit=2000&toTs={timestamp}"
    )
    r = perform_http_request(url)
    data = r["Data"]
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data
