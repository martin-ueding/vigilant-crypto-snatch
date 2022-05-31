import dataclasses
import datetime
from typing import Any
from typing import Dict
from typing import Optional

from ..core import AssetPair


class Trigger(object):
    def get_name(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    def fire(self, now: datetime.datetime) -> None:
        raise NotImplementedError()  # pragma: no cover

    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()  # pragma: no cover


@dataclasses.dataclass()
class TriggerSpec:
    asset_pair: AssetPair
    cooldown_minutes: int
    name: str
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

    def to_primitives(self) -> Dict[str, Any]:
        result = dict(
            coin=self.asset_pair.coin,
            fiat=self.asset_pair.fiat,
            cooldown_minutes=self.cooldown_minutes,
            name=self.name,
            delay_minutes=self.delay_minutes,
            drop_percentage=self.drop_percentage,
            volume_fiat=self.volume_fiat,
            percentage_fiat=self.percentage_fiat,
            start=self.start,
            fear_and_greed_index_below=self.fear_and_greed_index_below,
        )
        return {key: value for key, value in result.items() if value is not None}


class InvalidTriggerSpec(Exception):
    pass
