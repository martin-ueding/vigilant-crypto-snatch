import datetime

from vigilant_crypto_snatch.core import Price


class HistoricalSource(object):
    def get_price(self, then: datetime.datetime, coin: str, fiat: str) -> Price:
        raise NotImplementedError()


class HistoricalError(RuntimeError):
    pass
