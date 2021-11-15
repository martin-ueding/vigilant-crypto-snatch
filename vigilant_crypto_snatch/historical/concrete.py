import datetime
import typing

import requests

from . import HistoricalError
from . import HistoricalSource
from .. import core
from .. import datastorage
from .. import logger
from .. import marketplace


class CryptoCompareHistoricalSource(HistoricalSource):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_price(self, when: datetime.datetime, coin: str, fiat: str) -> core.Price:
        logger.debug(f"Retrieving historical price at {when} for {fiat}/{coin} …")
        timestamp = int(when.timestamp())
        kind = self.get_kind(when)
        url = self.base_url(kind, coin, fiat) + f"&limit=1&toTs={timestamp}"
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            raise HistoricalError(e)
        if r.status_code != 200:
            raise HistoricalError(
                f"The historical API has not returned a success: {r.status_code}"
            )
        j = r.json()
        if len(j["Data"]) == 0:
            raise HistoricalError(
                f"There is no payload from the historical API: {str(j)}"
            )
        close = j["Data"][-1]["close"]
        logger.debug(f"Retrieved a price of {close} at {when} from Cryptocompare.")
        return core.Price(timestamp=when, coin=coin, fiat=fiat, last=close)

    @staticmethod
    def get_kind(when: datetime.datetime) -> str:
        now = datetime.datetime.now()
        diff = now - when
        if diff < datetime.timedelta(hours=24):
            return "minute"
        elif diff < datetime.timedelta(days=30):
            return "hour"
        else:
            return "day"

    def base_url(self, kind: str, coin: str, fiat: str):
        return f"https://min-api.cryptocompare.com/data/histo{kind}?api_key={self.api_key}&fsym={coin.upper()}&tsym={fiat.upper()}"


class DatabaseHistoricalSource(HistoricalSource):
    def __init__(self, datastore: datastorage.Datastore, tolerance: datetime.timedelta):
        self.datastore = datastore
        self.tolerance = tolerance

    def get_price(self, when: datetime.datetime, coin: str, fiat: str) -> core.Price:
        price = self.datastore.get_price_around(when, coin, fiat, self.tolerance)
        if price is None:
            raise HistoricalError("Could not find entry in the database.")
        return price


class MarketSource(HistoricalSource):
    def __init__(self, market: marketplace.Marketplace):
        self.market = market

    def get_price(self, then: datetime.datetime, coin: str, fiat: str) -> core.Price:
        if then < datetime.datetime.now() - datetime.timedelta(seconds=30):
            raise HistoricalError(
                f"Cannot retrieve price that far in the past ({then})."
            )
        price = self.market.get_spot_price(coin, fiat, then)
        logger.debug(
            f"Retrieved a price of {price.last} at {then} from {self.market.get_name()}."
        )
        return price


class CachingHistoricalSource(HistoricalSource):
    def __init__(
        self,
        database_source: HistoricalSource,
        live_sources: typing.List[HistoricalSource],
        datastore: datastorage.Datastore,
    ):
        self.database_source = database_source
        self.live_sources = live_sources
        self.datastore = datastore

    def get_price(self, then: datetime.datetime, coin: str, fiat: str) -> core.Price:
        try:
            price = self.database_source.get_price(then, coin, fiat)
        except HistoricalError as e:
            logger.debug(e)
        else:
            logger.debug(f"Retrieved a price of {price} at {then} from the DB.")
            return price

        for live_source in self.live_sources:
            logger.debug(live_source)
            try:
                price = live_source.get_price(then, coin, fiat)
            except HistoricalError as e:
                logger.debug(f"Error from live source: {repr(e)}")
            else:
                self.datastore.add_price(price)
                return price

        raise HistoricalError("No source could deliver.")
