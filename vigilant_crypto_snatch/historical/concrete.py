import dataclasses
import datetime
import traceback
from typing import List

from .. import logger
from ..core import AssetPair
from ..core import Price
from ..datastorage import Datastore
from ..marketplace import Marketplace
from ..myrequests import HttpRequestError
from ..myrequests import perform_http_request
from .interface import HistoricalError
from .interface import HistoricalSource


@dataclasses.dataclass()
class CryptoCompareConfig:
    api_key: str


class CryptoCompareHistoricalSource(HistoricalSource):
    def __init__(self, config: CryptoCompareConfig):
        self.api_key = config.api_key

    def get_price(self, when: datetime.datetime, asset_pair: AssetPair) -> Price:
        logger.debug(
            f"Retrieving historical price at {when} for {asset_pair.fiat}/{asset_pair.coin} …"
        )
        timestamp = int(when.timestamp())
        kind = self.get_kind(when)
        url = self.base_url(kind, asset_pair) + f"&limit=1&toTs={timestamp}"
        try:
            j = perform_http_request(url)
        except HttpRequestError as e:
            raise HttpRequestError("HTTP error from Crypto Compare") from e
        if len(j["Data"]) == 0:
            raise HistoricalError(
                f"There is no payload from the historical API: {str(j)}"
            )
        close = j["Data"][-1]["close"]
        logger.debug(f"Retrieved a price of {close} at {when} from Cryptocompare.")
        return Price(timestamp=when, last=close, asset_pair=asset_pair)

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

    def base_url(self, kind: str, asset_pair: AssetPair):
        return f"https://min-api.cryptocompare.com/data/histo{kind}?api_key={self.api_key}&fsym={asset_pair.coin.upper()}&tsym={asset_pair.fiat.upper()}"


class DatabaseHistoricalSource(HistoricalSource):
    def __init__(self, datastore: Datastore, tolerance: datetime.timedelta):
        self.datastore = datastore
        self.tolerance = tolerance

    def get_price(self, when: datetime.datetime, asset_pair: AssetPair) -> Price:
        price = self.datastore.get_price_around(when, asset_pair, self.tolerance)
        if price is None:
            raise HistoricalError("Could not find entry in the database.")
        return price


class MarketSource(HistoricalSource):
    def __init__(self, market: Marketplace):
        self.market = market

    def get_price(self, then: datetime.datetime, asset_pair: AssetPair) -> Price:
        if then < datetime.datetime.now() - datetime.timedelta(seconds=30):
            raise HistoricalError(
                f"Cannot retrieve price that far in the past ({then}) from {self.market.get_name()}."
            )
        price = self.market.get_spot_price(asset_pair, then)
        logger.debug(
            f"Retrieved a price of {price.last} at {then} from {self.market.get_name()}."
        )
        return price


class CachingHistoricalSource(HistoricalSource):
    def __init__(
        self,
        database_source: HistoricalSource,
        live_sources: List[HistoricalSource],
        datastore: Datastore,
    ):
        self.database_source = database_source
        self.live_sources = live_sources
        self.datastore = datastore

    def get_price(self, then: datetime.datetime, asset_pair: AssetPair) -> Price:
        last_exception = None
        try:
            price = self.database_source.get_price(then, asset_pair)
        except HistoricalError as e:
            logger.debug(e)
            last_exception = e
        else:
            logger.debug(f"Retrieved a price of {price} at {then} from the DB.")
            return price

        for live_source in self.live_sources:
            logger.debug(live_source)
            try:
                price = live_source.get_price(then, asset_pair)
            except HistoricalError as e:
                logger.debug(f"Error from live source: {repr(e)}")
                last_exception = e
            else:
                self.datastore.add_price(price)
                return price

        raise HistoricalError("No source could deliver") from last_exception
