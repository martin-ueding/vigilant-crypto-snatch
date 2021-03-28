import datetime

from . import datamodel


class Marketplace(object):
    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        raise NotImplementedError()

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> datamodel.Price:
        raise NotImplementedError()

    def get_name(self) -> str:
        raise NotImplementedError()


class BuyError(Exception):
    pass


class TickerError(Exception):
    pass
