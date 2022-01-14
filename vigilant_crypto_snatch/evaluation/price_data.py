import datetime
import json
import os
from typing import List

import numpy as np
import pandas as pd
import scipy.interpolate

from .. import logger
from ..core import AssetPair
from ..core import Price
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

    def get_price(self, then: datetime.datetime, asset_pair: AssetPair) -> Price:
        try:
            last = self.interpolator(then.timestamp())
        except ValueError as e:
            raise HistoricalError(e)

        return Price(timestamp=then, last=last, asset_pair=asset_pair)


def get_hourly_data(asset_pair: AssetPair, api_key: str) -> List[dict]:
    cache_file = (
        f"~/.cache/vigilant-crypto-snatch/hourly_{asset_pair.coin}_{asset_pair.fiat}.js"
    )
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
    r = download_hourly_data(asset_pair, api_key)
    data = r["Data"]
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data


def download_hourly_data(asset_pair: AssetPair, api_key: str) -> dict:
    timestamp = int(datetime.datetime.now().timestamp())
    url = (
        f"https://min-api.cryptocompare.com/data/histohour"
        f"?api_key={api_key}"
        f"&fsym={asset_pair.coin}&tsym={asset_pair.fiat}"
        f"&limit=2000&toTs={timestamp}"
    )
    return perform_http_request(url)


def download_hourly_data_stub() -> dict:
    return {
        "Response": "Success",
        "Type": 100,
        "Aggregated": False,
        "TimeTo": 1640163600,
        "TimeFrom": 1640160000,
        "FirstValueInArray": True,
        "ConversionType": {"type": "direct", "conversionSymbol": ""},
        "Data": [
            {
                "time": 1630160000,
                "high": 43946.69,
                "low": 43612.18,
                "open": 43718.67,
                "volumefrom": 240.23,
                "volumeto": 10520019.65,
                "close": 43741.97,
                "conversionType": "direct",
                "conversionSymbol": "",
            },
            {
                "time": 1640163600,
                "high": 43781.93,
                "low": 43373.83,
                "open": 43741.97,
                "volumefrom": 216.59,
                "volumeto": 9445214.81,
                "close": 43419.35,
                "conversionType": "direct",
                "conversionSymbol": "",
            },
        ],
        "RateLimit": {},
        "HasWarning": False,
    }


def make_dataframe_from_json(data: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "time": elem["time"],
            "datetime": datetime.datetime.fromtimestamp(elem["time"]),
            "close": elem["close"],
        }
        for elem in data
    )
    return df


def make_test_dataframe() -> pd.DataFrame:
    response = download_hourly_data_stub()
    df = make_dataframe_from_json(response["Data"])
    return df
