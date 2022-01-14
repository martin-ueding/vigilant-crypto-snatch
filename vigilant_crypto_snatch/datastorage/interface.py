import datetime
from typing import *

from ..core import AssetPair
from ..core import Price
from ..core import Trade


class DatastoreException(Exception):
    pass


class Datastore:
    def add_price(self, price: Price) -> None:
        raise NotImplementedError()  # pragma: no cover

    def add_trade(self, trade: Trade) -> None:
        raise NotImplementedError()  # pragma: no cover

    def get_price_around(
        self,
        then: datetime.datetime,
        asset_pair: AssetPair,
        tolerance: datetime.timedelta,
    ) -> Optional[Price]:
        raise NotImplementedError()  # pragma: no cover

    def was_triggered_since(
        self, trigger_name: str, asset_pair: AssetPair, then: datetime.datetime
    ) -> bool:
        raise NotImplementedError()  # pragma: no cover

    def get_all_prices(self) -> List[Price]:
        raise NotImplementedError()  # pragma: no cover

    def get_all_trades(self) -> List[Trade]:
        raise NotImplementedError()  # pragma: no cover

    def clean_old(self, before: datetime.datetime) -> None:
        raise NotImplementedError()  # pragma: no cover
