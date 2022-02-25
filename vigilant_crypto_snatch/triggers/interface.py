import dataclasses
import datetime
from typing import Optional

from ..core import AssetPair


class Trigger(object):
    def get_name(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    def fire(self, now: datetime.datetime) -> None:
        raise NotImplementedError()  # pragma: no cover

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()  # pragma: no cover

    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()  # pragma: no cover


@dataclasses.dataclass()
class TriggerSpec:
    asset_pair: AssetPair
    cooldown_minutes: int
    name: Optional[str] = None
    delay_minutes: Optional[int] = None
    drop_percentage: Optional[float] = None
    volume_fiat: Optional[float] = None
    percentage_fiat: Optional[float] = None
    start: Optional[datetime.datetime] = None
    fear_and_greed_index_below: Optional[int] = None

    def __post_init__(self):
        if self.cooldown_minutes <= 0:
            raise InvalidTriggerSpec("The cooldown must be a positive number.")
        if self.delay_minutes is not None and self.delay_minutes <= 0:
            raise InvalidTriggerSpec("The delay must be a positive number.")

        if self.drop_percentage and not self.delay_minutes:
            raise InvalidTriggerSpec(
                "You have specified a drop percentage, but not a delay."
            )
        if not self.drop_percentage and self.delay_minutes:
            raise InvalidTriggerSpec(
                "You have specified a delay, but not a drop percentage."
            )


class InvalidTriggerSpec(Exception):
    pass
