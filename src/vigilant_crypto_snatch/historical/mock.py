import datetime
import math

from .. import core
from .. import historical

reference_time = datetime.datetime(2021, 1, 1, 00, 00, 00)


def mock_price(then: datetime.datetime):
    t = (then - reference_time).total_seconds()
    amount = (
        10000 * math.exp(t / (3600 * 24 * 365))
        + 1000 * math.cos(t / (3600 * 24 * 14))
        + 100 * math.cos(t / (500 * math.pi))
    )
    return amount


class MockHistorical(historical.HistoricalSource):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def get_price(self, then: datetime.datetime, coin: str, fiat: str) -> core.Price:
        self.calls += 1
        return core.Price(
            timestamp=then,
            last=mock_price(then),
            coin=coin,
            fiat=fiat,
        )
