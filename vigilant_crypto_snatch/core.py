import dataclasses
import datetime
from typing import Optional


@dataclasses.dataclass()
class Price:
    timestamp: datetime.datetime
    last: float
    coin: str
    fiat: str

    def __str__(self):
        return f"{self.timestamp}: {self.last} {self.fiat}/{self.coin}"


@dataclasses.dataclass()
class Trade:
    timestamp: datetime.datetime
    trigger_name: str
    volume_coin: float
    volume_fiat: float
    coin: str
    fiat: str

    def __repr__(self):
        return (
            f"Trade("
            f"timestamp={repr(self.timestamp)}, "
            f"trigger_name={repr(self.trigger_name)}, "
            f"volume_coin={repr(self.volume_coin)}, "
            f"volume_fiat={repr(self.volume_fiat)}, "
            f"coin={repr(self.coin)}, "
            f"fiat={repr(self.fiat)}"
            f")"
        )

    def to_dict(self) -> dict:
        return dict(
            timestamp=self.timestamp,
            trigger_name=self.trigger_name,
            volume_coin=self.volume_coin,
            volume_fiat=self.volume_fiat,
            coin=self.coin,
            fiat=self.fiat,
        )


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
