import datetime
import logging
import typing

import requests
import sqlalchemy.orm

from . import datamodel
from . import marketplace


logger = logging.getLogger("vigilant_crypto_snatch")


class HistoricalSource(object):
    def get_price(
        self, then: datetime.datetime, coin: str, fiat: str
    ) -> datamodel.Price:
        raise NotImplementedError()


class HistoricalError(RuntimeError):
    pass


class CryptoCompareHistoricalSource(HistoricalSource):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_price(
        self, when: datetime.datetime, coin: str, fiat: str
    ) -> datamodel.Price:
        logger.debug(f"Retrieving historical price at {when} for {fiat}/{coin} …")
        timestamp = int(when.timestamp())
        kind = self.get_kind(when)
        url = self.base_url(kind, coin, fiat) + "&limit=1&toTs={timestamp}"
        r = requests.get(url)
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
        return datamodel.Price(timestamp=when, coin=coin, fiat=fiat, last=close)

    def get_kind(self, when: datetime.datetime) -> str:
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
    def __init__(self, session: sqlalchemy.orm.session, tolerance: datetime.timedelta):
        self.session = session
        self.tolerance = tolerance

    def get_price(
        self, when: datetime.datetime, coin: str, fiat: str
    ) -> datamodel.Price:
        try:
            q = (
                self.session.query(datamodel.Price)
                .filter(
                    datamodel.Price.timestamp < when,
                    datamodel.Price.coin == coin,
                    datamodel.Price.fiat == fiat,
                )
                .order_by(datamodel.Price.timestamp.desc())[0]
            )
            if q.timestamp > when - self.tolerance:
                logger.debug(
                    f"Found historical price for {when} in database: {q.last} {fiat}/{coin}."
                )
                return q
        except sqlalchemy.orm.exc.NoResultFound:
            pass
        except IndexError:
            pass

        raise HistoricalError("Could not find entry in the database.")


class MarketSource(HistoricalSource):
    def __init__(self, market: marketplace.Marketplace):
        self.market = market

    def get_price(
        self, then: datetime.datetime, coin: str, fiat: str
    ) -> datamodel.Price:
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
        session: sqlalchemy.orm.session,
    ):
        self.database_source = database_source
        self.live_sources = live_sources
        self.session = session

    def get_price(
        self, then: datetime.datetime, coin: str, fiat: str
    ) -> datamodel.Price:
        try:
            price = self.database_source.get_price(then, coin, fiat)
        except HistoricalError as e:
            logger.debug(e)
        else:
            logger.debug(f"Retrieved a price of {price} at {then} from the DB.")
            return price

        for live_source in self.live_sources:
            try:
                price = live_source.get_price(then, coin, fiat)
            except HistoricalError as e:
                logger.debug(e)
            else:
                self.session.add(price)
                self.session.commit()
                return price

        raise HistoricalError("No source could deliver.")
