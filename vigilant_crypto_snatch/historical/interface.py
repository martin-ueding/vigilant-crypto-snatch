import datetime

from ..core import AssetPair
from ..core import Price


class HistoricalSource(object):
    def get_price(self, then: datetime.datetime, asset_pair: AssetPair) -> Price:
        raise NotImplementedError()  # pragma: no cover


class HistoricalError(RuntimeError):
    pass
