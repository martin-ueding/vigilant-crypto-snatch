import datetime

from .. import core


class HistoricalSource(object):
    def get_price(self, then: datetime.datetime, coin: str, fiat: str) -> core.Price:
        raise NotImplementedError()


class HistoricalError(RuntimeError):
    pass
