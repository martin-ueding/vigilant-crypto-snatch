import datetime
from typing import List
from typing import Tuple

import numpy as np
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


def accumulate_value(
    data,
    data_datetime,
    selection,
    trades,
    trigger_names,
    progress_callback=lambda n: None,
) -> pd.DataFrame:
    result = []
    for i, elem in enumerate(data_datetime.loc[selection]):
        for trigger_name in trigger_names:
            sel1 = trades["timestamp"] <= elem
            sel2 = trades["trigger_name"] == trigger_name
            sel12 = sel1 & sel2
            cumsum_coin = np.sum(trades["volume_coin"][sel12])
            cumsum_fiat = np.sum(trades["volume_fiat"][sel12])
            value_fiat = cumsum_coin * data.loc[i, "close"]
            result.append(
                dict(
                    datetime=elem,
                    trigger_name=trigger_name,
                    cumsum_coin=cumsum_coin,
                    cumsum_fiat=cumsum_fiat,
                    value_fiat=value_fiat,
                )
            )
        progress_callback((i + 1) / len(data_datetime.loc[selection]))
    value = pd.DataFrame(result)
    return value
