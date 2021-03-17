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
    def get_price(
        self, then: datetime.datetime, coin: str, fiat: str
    ) -> vigilant_crypto_snatch.datamodel.Price:
        return vigilant_crypto_snatch.datamodel.Price(
            timestamp=then,
            last=mock_price(then),
            coin=coin,
            fiat=fiat,
        )


class MockMarketplace(vigilant_crypto_snatch.marketplace.Marketplace):
    def get_spot_price(
        self, coin: str, fiat: str
    ) -> vigilant_crypto_snatch.datamodel.Price:
        then = datetime.datetime.now()
        return vigilant_crypto_snatch.datamodel.Price(
            timestamp=then,
            last=mock_price(then),
            coin=coin,
            fiat=fiat,
        )
