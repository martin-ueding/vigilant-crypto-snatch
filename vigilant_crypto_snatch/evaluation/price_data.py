import datetime
import json
import os
from typing import List

import numpy as np
import pandas as pd
import scipy.interpolate

from .. import logger
from ..core import Price
from ..datastorage import Datastore
from ..historical import HistoricalError
from ..historical import HistoricalSource
from ..myrequests import perform_http_request


def make_interpolator(data: pd.DataFrame):
    x = data["time"]
    y = data["close"]
    return scipy.interpolate.interp1d(x, y)


class InterpolatingSource(HistoricalSource):
    def __init__(self, data: pd.DataFrame):
        self.interpolator = make_interpolator(data)
        self.start = np.min(data["datetime"])
        self.end = np.max(data["datetime"])

    def get_price(self, then: datetime.datetime, coin: str, fiat: str) -> Price:
        try:
            last = self.interpolator(then.timestamp())
        except ValueError as e:
            raise HistoricalError(e)

        return Price(
            timestamp=then,
            last=last,
            coin=coin,
            fiat=fiat,
        )


def json_to_database(
    data: List[dict], coin: str, fiat: str, datastore: Datastore
) -> None:
    logger.info(f"Writing {len(data)} prices to the DB …")
    for elem in data:
        price = Price(
            timestamp=datetime.datetime.fromtimestamp(elem["time"]),
            last=elem["close"],
            coin=coin,
            fiat=fiat,
        )
        datastore.add_price(price)


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


def make_dataframe_from_json(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "time": data["time"],
            "datetime": list(map(datetime.datetime.fromtimestamp, data["time"])),
            "close": data["close"],
        }
    )
    return df
