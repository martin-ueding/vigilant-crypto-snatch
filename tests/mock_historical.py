import datetime
import math

import vigilant_crypto_snatch.historical
import vigilant_crypto_snatch.datamodel
import vigilant_crypto_snatch.marketplace

reference_time = datetime.datetime(2021, 1, 1, 00, 00, 00)


def mock_price(then: datetime.datetime):
    t = (then - reference_time).total_seconds()
    amount = (
        10000 * math.exp(t / (3600 * 24 * 365))
        + 1000 * math.cos(t / (3600 * 24 * 14))
        + 100 * math.cos(t / (500 * math.pi))
    )
    return amount


class MockHistorical(vigilant_crypto_snatch.historical.HistoricalSource):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def get_price(
        self, then: datetime.datetime, coin: str, fiat: str
    ) -> vigilant_crypto_snatch.datamodel.Price:
        self.calls += 1
        return vigilant_crypto_snatch.datamodel.Price(
            timestamp=then,
            last=mock_price(then),
            coin=coin,
            fiat=fiat,
        )


class MockMarketplace(vigilant_crypto_snatch.marketplace.Marketplace):

    def __init__(self):
        super().__init__()
        self.orders = 0
        self.prices = 0
        self.balances = {'EUR': 1000.0}

    def get_balance(self) -> dict:
        return self.balances

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        self.orders += 1

    def get_name(self) -> str:
        return "Mock"

    def get_spot_price(
        self, coin: str, fiat: str, now: datetime.datetime
    ) -> vigilant_crypto_snatch.datamodel.Price:
        self.prices += 1
        then = datetime.datetime.now()
        return vigilant_crypto_snatch.datamodel.Price(
            timestamp=then,
            last=mock_price(then),
            coin=coin,
            fiat=fiat,
        )
