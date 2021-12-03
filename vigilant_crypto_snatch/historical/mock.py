import datetime
import math

from ..core import Price
from .interface import HistoricalSource

reference_time = datetime.datetime(2021, 1, 1, 00, 00, 00)


def mock_price(then: datetime.datetime):
    t = (then - reference_time).total_seconds()
    amount = (
        10000 * math.exp(t / (3600 * 24 * 365))
        + 1000 * math.cos(t / (3600 * 24 * 14))
        + 100 * math.cos(t / (500 * math.pi))
    )
    return amount


class MockHistorical(HistoricalSource):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def get_price(self, then: datetime.datetime, coin: str, fiat: str) -> Price:
        self.calls += 1
        return Price(
            timestamp=then,
            last=mock_price(then),
            coin=coin,
            fiat=fiat,
        )
