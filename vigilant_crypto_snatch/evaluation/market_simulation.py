import datetime
from typing import List
from typing import Tuple

import altair as alt
import numpy as np
import pandas as pd

from ..core import AssetPair
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

    def place_order(self, asset_pair: AssetPair, volume: float) -> None:
        pass

    def get_name(self) -> str:
        return "Simulation"

    def get_spot_price(self, asset_pair: AssetPair, now: datetime.datetime) -> Price:
        return self.source.get_price(now, asset_pair)


def simulate_triggers(
    data: pd.DataFrame,
    assert_pair: AssetPair,
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
            if not (trigger.asset_pair == assert_pair):
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
    data: pd.DataFrame,
    trades: pd.DataFrame,
    trigger_names: List[str],
    progress_callback=lambda n: None,
) -> pd.DataFrame:
    result = []
    for i, elem in enumerate(data["datetime"]):
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
        progress_callback((i + 1) / len(data["datetime"]))
    value = pd.DataFrame(result)
    return value


def summarize_simulation(
    data: pd.DataFrame,
    trades: pd.DataFrame,
    value: pd.DataFrame,
    trigger_names: List[str],
    asset_pair: AssetPair,
) -> pd.DataFrame:
    summary_rows = []
    for trigger_name in trigger_names:
        sub_trades = trades[trades["trigger_name"] == trigger_name]
        sub_values = value[value["trigger_name"] == trigger_name]
        num_trigger_executions = len(sub_trades)
        cumsum_fiat = sub_values["cumsum_fiat"].iat[-1]
        cumsum_coin = sub_values["cumsum_coin"].iat[-1]
        value_fiat = sub_values["value_fiat"].iat[-1]
        average_price = cumsum_fiat / cumsum_coin
        gain = value_fiat / cumsum_fiat - 1
        period = (data["datetime"].iat[-1] - data["datetime"].iat[0]).days
        yearly_gain = np.power(gain + 1, 365 / period) - 1
        row = {
            "Trigger": trigger_name,
            "Days": period,
            "Trades": num_trigger_executions,
            f"{asset_pair.fiat} invested": cumsum_fiat,
            f"{asset_pair.coin} acquired": cumsum_coin,
            f"{asset_pair.fiat} value": value_fiat,
            f"Average {asset_pair.fiat}/{asset_pair.coin}": average_price,
            "Gain %": gain,
            "Gain %/a": yearly_gain,
        }
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)
    return summary


def make_gain_chart(value: pd.DataFrame, fiat: str) -> alt.Chart:
    value_long = value.rename(
        {"cumsum_fiat": "Invested", "value_fiat": "Value"}, axis=1
    ).melt(["datetime", "trigger_name"], ["Invested", "Value"])

    chart = (
        alt.Chart(value_long)
        .mark_line()
        .encode(
            x=alt.X("datetime", title="Time"),
            y=alt.Y("value", title=f"{fiat}"),
            strokeDash=alt.StrokeDash(
                "variable", title="Variable", legend=alt.Legend(orient="bottom")
            ),
            color=alt.Color(
                "trigger_name", title="Trigger", legend=alt.Legend(orient="bottom")
            ),
        )
        .interactive()
    )
    return chart
