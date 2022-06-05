import datetime
from typing import Optional

import pandas as pd

from ...configuration import Configuration
from ...core import AssetPair
from ...evaluation import accumulate_value
from ...evaluation import get_hourly_data
from ...evaluation import make_dataframe_from_json
from ...evaluation import simulate_triggers
from ...evaluation import summarize_simulation
from ...feargreed import AlternateMeFearAndGreedIndex
from ...triggers import TriggerSpec
from ..ui.simulation import SimulationTab
from .charts import make_qt_chart_from_data_frame
from .configuration import SingleTriggerEditController
from .report import PandasTableModel


class SimulationTabController:
    def __init__(self, ui: SimulationTab):
        self.ui = ui
        self.spec = TriggerSpec(
            name="Simulated Trigger",
            asset_pair=AssetPair("BTC", "EUR"),
            cooldown_minutes=24 * 3600,
            volume_fiat=100,
        )
        self.trigger_edit_controller = SingleTriggerEditController(
            self.ui.trigger_pane, self.spec
        )
        self.ui.simulate.clicked.connect(self.simulate)
        self.config: Optional[Configuration] = None
        self.trade_table_model = PandasTableModel()
        self.ui.trade_table.setModel(self.trade_table_model)
        self.summary_table_model = PandasTableModel()
        self.ui.summary_table.setModel(self.summary_table_model)
        self.simulations = pd.DataFrame()

    def set_config(self, config: Configuration):
        self.config = config

    def simulate(self):
        self.ui.progress_bar_1.setValue(0)
        self.trigger_edit_controller.get_spec()
        asset_pair = self.spec.asset_pair
        data = get_hourly_data(asset_pair, self.config.crypto_compare.api_key)
        data = make_dataframe_from_json(data)
        data["label"] = "Close price"

        close_chart = make_qt_chart_from_data_frame(
            data.rename(columns={"close": "value"}), self.spec.asset_pair.fiat
        )
        self.ui.close_chart.setChart(close_chart)

        fear_greed_access = AlternateMeFearAndGreedIndex()
        date_range = pd.date_range(
            min(data["datetime"]).date(), max(data["datetime"]).date()
        )
        today = datetime.date.today()
        fear_greed_df = pd.DataFrame(
            {
                "datetime": date_range,
                "value": [
                    fear_greed_access.get_value(date.date(), today)
                    for date in date_range
                ],
            }
        )
        fear_greed_df["label"] = "Fear & Greed"

        feargreed_chart = make_qt_chart_from_data_frame(fear_greed_df, "Index")
        self.ui.fear_and_greed_chart.setChart(feargreed_chart)

        trades, trigger_names = simulate_triggers(
            data,
            self.spec.asset_pair,
            [self.spec],
            lambda fraction: self.ui.progress_bar_2.setValue(int(fraction * 100)),
        )
        self.ui.progress_bar_1.setValue(50)
        self.trade_table_model.set_data_frame(trades)

        value = accumulate_value(
            data,
            trades,
            trigger_names,
            lambda fraction: self.ui.progress_bar_2.setValue(int(fraction * 100)),
        )
        self.ui.progress_bar_1.setValue(100)

        summary = summarize_simulation(
            data,
            trades,
            value,
            trigger_names,
            self.spec.asset_pair,
        )
        value_long = (
            value.rename({"cumsum_fiat": "Invested", "value_fiat": "Value"}, axis=1)
            .melt(["datetime", "trigger_name"], ["Invested", "Value"])
            .rename(columns={"variable": "label"})
        )
        gain_chart = make_qt_chart_from_data_frame(
            value_long, self.spec.asset_pair.fiat
        )
        self.ui.gain_chart.setChart(gain_chart)

        self.simulations = pd.concat([self.simulations, summary])
        self.summary_table_model.set_data_frame(self.simulations)
