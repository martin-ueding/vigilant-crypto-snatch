import datetime
from typing import Optional

from .. import logger
from ..core import AssetPair
from ..datastorage import Datastore
from ..feargreed import FearAndGreedIndex
from ..historical import HistoricalError
from ..historical import HistoricalSource
from ..marketplace import Marketplace


class TriggeredDelegate(object):
    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()  # pragma: no cover

    def format_stall_reason(self, now: datetime.datetime) -> Optional[str]:
        raise NotImplementedError()  # pragma: no cover


class StartTriggeredDelegate(TriggeredDelegate):
    def __init__(self, start: datetime.datetime):
        self.start = start

    def is_triggered(self, now: datetime.datetime) -> bool:
        return self.start <= now

    def __str__(self) -> str:
        return f"StartTriggeredDelegate(start={self.start})"

    def format_stall_reason(self, now: datetime.datetime) -> Optional[str]:
        if not self.is_triggered(now):
            return f"Start ({self.start.isoformat()}) is not reached yet."
        else:
            return None


class CooldownTriggeredDelegate(TriggeredDelegate):
    def __init__(
        self,
        cooldown_minutes: int,
        datastore: Datastore,
        asset_pair: AssetPair,
        name: str,
    ):
        self.cooldown_minutes = cooldown_minutes
        self.datastore = datastore
        self.asset_pair = asset_pair
        self.name = name

    def is_triggered(self, now: datetime.datetime) -> bool:
        then = now - datetime.timedelta(minutes=self.cooldown_minutes)
        return not self.datastore.was_triggered_since(self.name, self.asset_pair, then)

    def __str__(self) -> str:
        return f"CooldownTriggeredDelegate({self.cooldown_minutes} minutes)"

    def format_stall_reason(self, now: datetime.datetime) -> Optional[str]:
        if not self.is_triggered(now):
            return "Cooldown not over yet."
        else:
            return None


class DropTriggeredDelegate(TriggeredDelegate):
    def __init__(
        self,
        asset_pair: AssetPair,
        delay_minutes: int,
        drop_percentage: float,
        source: HistoricalSource,
    ):
        self.asset_pair = asset_pair
        self.delay_minutes = delay_minutes
        self.drop_percentage = drop_percentage
        self.source = source

    def is_triggered(self, now: datetime.datetime) -> bool:
        price = self.source.get_price(now, self.asset_pair)
        then = now - datetime.timedelta(minutes=self.delay_minutes)
        try:
            then_price = self.source.get_price(then, self.asset_pair)
        except HistoricalError as e:
            logger.warning(
                f"Could not retrieve a historical price, so cannot determine if strategy “{self}” was triggered."
                f" The original error is: {e}"
            )
            return False
        critical = float(then_price.last) * (1 - self.drop_percentage / 100)
        return price.last < critical

    def __str__(self) -> str:
        return f"Drop(delay_minutes={self.delay_minutes}, drop={self.drop_percentage})"  # pragma: no cover

    def format_stall_reason(self, now: datetime.datetime) -> Optional[str]:
        if not self.is_triggered(now):
            then = now - datetime.timedelta(minutes=self.delay_minutes)
            then_price = self.source.get_price(then, self.asset_pair)
            return f"Old price ({then_price}) is too high."
        else:
            return None


class FearAndGreedIndexTriggeredDelegate(TriggeredDelegate):
    def __init__(self, threshold: int, index: FearAndGreedIndex):
        self.threshold = threshold
        self.index = index

    def is_triggered(self, now: datetime.datetime) -> bool:
        value = self.index.get_value(now.date(), now.date())
        return value < self.threshold

    def __str__(self) -> str:
        return (
            f"FearAndGreedIndexTriggeredDelegate({self.threshold})"  # pragma: no cover
        )

    def format_stall_reason(self, now: datetime.datetime) -> Optional[str]:
        if not self.is_triggered(now):
            value = self.index.get_value(now.date(), now.date())
            return f"Fear & Greed index ({value}) is higher than threshold ({self.threshold})."
        else:
            return None


class SufficientFundsTriggeredDelegate(TriggeredDelegate):
    def __init__(self, required_fiat: float, fiat: str, marketplace: Marketplace):
        self.fiat = fiat
        self.required_fiat = required_fiat
        self.marketplace = marketplace

    def is_triggered(self, now: datetime.datetime) -> bool:
        try:
            balances = self.marketplace.get_balance()
            return balances[self.fiat] >= self.required_fiat
        except NotImplementedError:
            return True
