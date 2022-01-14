import datetime

from .. import logger
from ..core import AssetPair
from ..feargreed import FearAndGreedIndex
from ..historical import HistoricalError
from ..historical import HistoricalSource


class TriggeredDelegate(object):
    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()  # pragma: no cover


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


class TrueTriggeredDelegate(TriggeredDelegate):
    def is_triggered(self, now: datetime.datetime) -> bool:
        return True

    def __str__(self) -> str:
        return f"True()"  # pragma: no cover


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
