import dataclasses
import datetime


@dataclasses.dataclass()
class AssetPair:
    coin: str
    fiat: str

    def __hash__(self) -> int:
        return hash((self.coin, self.fiat))


@dataclasses.dataclass()
class Price:
    timestamp: datetime.datetime
    last: float
    asset_pair: AssetPair

    def __str__(self):
        return f"{self.timestamp}: {self.last} {self.asset_pair.fiat}/{self.asset_pair.coin}"


@dataclasses.dataclass()
class Trade:
    timestamp: datetime.datetime
    trigger_name: str
    volume_coin: float
    volume_fiat: float
    asset_pair: AssetPair

    def __repr__(self):
        return (
            f"Trade("
            f"timestamp={repr(self.timestamp)}, "
            f"trigger_name={repr(self.trigger_name)}, "
            f"volume_coin={repr(self.volume_coin)}, "
            f"volume_fiat={repr(self.volume_fiat)}, "
            f"coin={repr(self.asset_pair.coin)}, "
            f"fiat={repr(self.asset_pair.fiat)}"
            f")"
        )

    def to_dict(self) -> dict:
        return dict(
            timestamp=self.timestamp,
            trigger_name=self.trigger_name,
            volume_coin=self.volume_coin,
            volume_fiat=self.volume_fiat,
            coin=self.asset_pair.coin,
            fiat=self.asset_pair.fiat,
        )
