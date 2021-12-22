import datetime

from ..core import Price
from ..historical import HistoricalSource
from ..marketplace import Marketplace


class SimulationMarketplace(Marketplace):
    def __init__(self, source: HistoricalSource):
        super().__init__()
        self.source = source

    def place_order(self, coin: str, fiat: str, volume: float) -> None:
        pass

    def get_name(self) -> str:
        return "Simulation"

    def get_spot_price(self, coin: str, fiat: str, now: datetime.datetime) -> Price:
        return self.source.get_price(now, coin, fiat)
