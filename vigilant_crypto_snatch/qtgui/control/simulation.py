import threading
from typing import List
from typing import Optional

from ...configuration import Configuration
from ...core import AssetPair
from ...datastorage import make_datastore
from ...evaluation import accumulate_value
from ...evaluation import get_hourly_data
from ...evaluation import InterpolatingSource
from ...evaluation import make_dataframe_from_json
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
        thread = threading.Thread(target=self.simulation_worker)
        thread.start()

    def simulation_worker(self):
        self.trigger_edit_controller.get_spec()
        asset_pair = self.spec.asset_pair
        data = get_hourly_data(asset_pair, self.config.crypto_compare.api_key)
        data = make_dataframe_from_json(data)
        trades, trigger_names = simulate_triggers(
            data,
            self.spec.asset_pair,
            [self.spec],
            # lambda fraction: self.ui.progress_bar.setValue(int(fraction * 100)),
        )
        self.trade_table_model.set_data_frame(trades)

        value = accumulate_value(data, trades, trigger_names, print)

        summary = summarize_simulation(
            data,
            trades,
            value,
            trigger_names,
            self.spec.asset_pair,
        )

        self.gain_chart = make_gain_chart(value, self.spec.asset_pair.fiat)
        # self.ui.gain_chart.updateChart(self.gain_chart)
