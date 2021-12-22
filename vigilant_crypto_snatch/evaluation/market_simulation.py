import datetime
from typing import List
from typing import Tuple

import pandas as pd

from ..core import Price
from ..datastorage import make_datastore
from ..historical import HistoricalError
from ..historical import HistoricalSource
from ..marketplace import Marketplace
from ..triggers import make_buy_trigger
from ..triggers import TriggerSpec
from .price_data import InterpolatingSource


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


def simulate_triggers(
    data: pd.DataFrame,
    coin: str,
    fiat: str,
    trigger_specs: List[TriggerSpec],
    progress_callback=lambda n: None,
) -> Tuple[pd.DataFrame, List[str]]:
    datastore = make_datastore(None)
    source = InterpolatingSource(data)
    market = SimulationMarketplace(source)

    active_triggers = [
        make_buy_trigger(datastore, source, market, trigger_spec)
        for trigger_spec in trigger_specs
    ]

    for i in data.index:
        row = data.loc[i]
        now = row["datetime"]
        for trigger in active_triggers:
            if not (trigger.coin == coin and trigger.fiat == fiat):
                continue
            try:
                if trigger.is_triggered(now):
                    if trigger.has_cooled_off(now):
                        trigger.fire(now)
                    else:
                        pass
            except HistoricalError as e:
                pass
        progress_callback((i + 1) / len(data))

    all_trades = datastore.get_all_trades()
    trade_df = pd.DataFrame([trade.to_dict() for trade in all_trades])
    trigger_names = [trigger.get_name() for trigger in active_triggers]
    return trade_df, trigger_names
