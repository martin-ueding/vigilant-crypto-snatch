import datetime
import typing

import numpy as np
import pandas as pd
import scipy.interpolate
import sqlalchemy.orm

from . import datamodel
from . import historical
from . import marketplace
from . import logger


def make_interpolator(data: pd.DataFrame):
    x = data["time"]
    y = data["close"]
    return scipy.interpolate.interp1d(x, y)


class InterpolatingSource(historical.HistoricalSource):
    def __init__(self, data: pd.DataFrame):
        self.interpolator = make_interpolator(data)
        self.start = np.min(data["datetime"])
        self.end = np.max(data["datetime"])

    def get_price(
        self, then: datetime.datetime, coin: str, fiat: str
    ) -> datamodel.Price:
        try:
            last = self.interpolator(then.timestamp())
        except ValueError as e:
            raise historical.HistoricalError(e)

        return datamodel.Price(
            timestamp=then,
            last=last,
            coin=coin,
            fiat=fiat,
        )


def json_to_database(
    data: typing.List[dict], coin: str, fiat: str, session: sqlalchemy.orm.session
) -> None:
    logger.info(f"Writing {len(data)} prices to the DB …")
    for elem in data:
        price = datamodel.Price(
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
) -> typing.Tuple[np.array, np.array, np.array]:
    factor = np.zeros(hours.shape + drops.shape)
    for i, hour in enumerate(hours):
        for j, drop in enumerate(drops):
            factor[i, j] = compute_gains(data, hour, drop)[2]
    return hours, drops, factor.T


def compute_gains(
    df: pd.DataFrame, hours: int, drop: float
) -> typing.Tuple[float, float, float]:
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


class SimulationMarketplace(marketplace.Marketplace):
    def __init__(self, source: historical.HistoricalSource):
        super().__init__()
        self.source = source

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        pass

    def get_name(self) -> str:
        return "Simulation"

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> datamodel.Price:
        return self.source.get_price(now, coin, fiat)
