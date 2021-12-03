import datetime
from typing import List
from typing import Tuple

import numpy as np
import pandas as pd
import scipy.interpolate
import sqlalchemy.orm

from . import logger
from .core import Price
from .historical import HistoricalError
from .historical import HistoricalSource
from .marketplace import Marketplace


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
    data: List[dict], coin: str, fiat: str, session: sqlalchemy.orm.session.Session
) -> None:
    logger.info(f"Writing {len(data)} prices to the DB …")
    for elem in data:
        price = Price(
            timestamp=datetime.datetime.fromtimestamp(elem["time"]),
            last=elem["close"],
            coin=coin,
            fiat=fiat,
        )
        session.add(price)
    session.commit()


def make_dataframe_from_json(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data)
    df["datetime"] = list(map(datetime.datetime.fromtimestamp, df["time"]))
    return df


def drop_survey(
    data: pd.DataFrame, hours, drops
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    factor = np.zeros(hours.shape + drops.shape)
    for i, hour in enumerate(hours):
        for j, drop in enumerate(drops):
            factor[i, j] = compute_gains(data, hour, drop)[2]
    return hours, drops, factor.T


def compute_gains(
    df: pd.DataFrame, hours: int, drop: float
) -> Tuple[float, float, float]:
    close_shift = df["close"].shift(hours)
    ratio = df["close"] / close_shift
    btc = 0.0
    eur = 0.0
    last = -hours
    for i in range(len(df)):
        if ratio[i] < (1 - drop) and last + hours <= i:
            last = i
            btc += 1.0 / df["close"][i]
            eur += 1.0
    return btc, eur, btc / eur if eur > 0 else 0.0


class SimulationMarketplace(Marketplace):
    def __init__(self, source: HistoricalSource):
        super().__init__()
        self.source = source

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        pass

    def get_name(self) -> str:
        return "Simulation"

    def get_spot_price(self, coin: str, fiat: str, now: datetime.datetime) -> Price:
        return self.source.get_price(now, coin, fiat)
