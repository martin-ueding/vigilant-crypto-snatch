import dataclasses
import datetime
from typing import Optional


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
    coin: str
    fiat: str
    cooldown_minutes: int
    name: Optional[str] = None
    delay_minutes: Optional[int] = None
    drop_percentage: Optional[float] = None
    volume_fiat: Optional[float] = None
    percentage_fiat: Optional[float] = None
    start: Optional[datetime.datetime] = None
    fear_and_greed_index_below: Optional[int] = None
