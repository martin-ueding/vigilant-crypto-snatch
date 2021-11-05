import datetime
from typing import *

import vigilant_crypto_snatch.core


class Datastore:
    def get_price_around(
        self, then: datetime.datetime, tolerance: datetime.timedelta
    ) -> vigilant_crypto_snatch.core.Price:
        raise NotImplementedError()

    def was_triggered_since(self, trigger_name: str, then: datetime.datetime) -> bool:
        raise NotImplementedError()

    def get_all_trades(self) -> List[vigilant_crypto_snatch.core.Price]:
        raise NotImplementedError()

    def clean_old(self, before: datetime.datetime):
        raise NotImplementedError()
