import datetime
from typing import *

from vigilant_crypto_snatch import core
from vigilant_crypto_snatch import triggers


class Datastore:
    def add_price(self, price: core.Price) -> None:
        raise NotImplementedError()

    def add_trade(self, trade: core.Trade) -> None:
        raise NotImplementedError()

    def get_price_around(
        self, then: datetime.datetime, tolerance: datetime.timedelta
    ) -> core.Price:
        raise NotImplementedError()

    def was_triggered_since(
        self, trigger: triggers.BuyTrigger, then: datetime.datetime
    ) -> bool:
        raise NotImplementedError()

    def get_all_trades(self) -> List[core.Price]:
        raise NotImplementedError()

    def clean_old(self, before: datetime.datetime):
        raise NotImplementedError()
