import threading
from typing import List
from typing import Optional

import numpy as np
import pandas as pd

from ...configuration import Configuration
from ...core import AssetPair
from ...datastorage import make_datastore
from ...evaluation import accumulate_value
from ...evaluation import get_hourly_data
from ...evaluation import InterpolatingSource
from ...evaluation import make_close_chart
from ...evaluation import make_dataframe_from_json
from ...evaluation import make_fear_greed_chart
from ...evaluation import make_gain_chart
from ...evaluation import simulate_triggers
from ...evaluation import SimulationMarketplace
from ...evaluation import summarize_simulation
from ...triggers import BuyTrigger
from ...triggers import make_buy_trigger
from ...triggers import TriggerSpec
from ..ui.simulation import SimulationTab
from .configuration import SingleTriggerEditController
from .configuration import TriggerPaneController
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

    def set_config(self, config: Configuration):
        self.config = config

    def simulate(self):
        self.ui.progress_bar_1.setValue(0)
        self.trigger_edit_controller.get_spec()
        asset_pair = self.spec.asset_pair
        data = get_hourly_data(asset_pair, self.config.crypto_compare.api_key)
        data = make_dataframe_from_json(data)

        close_chart = make_close_chart(data, asset_pair)
        self.ui.close_chart.set_chart(close_chart)

        feargreed_chart = make_fear_greed_chart(
            min(data["datetime"]), max(data["datetime"])
        )
        self.ui.fear_and_greed_chart.set_chart(feargreed_chart)

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

        self.gain_chart = make_gain_chart(value, self.spec.asset_pair.fiat)
        self.ui.gain_chart.set_chart(self.gain_chart)
