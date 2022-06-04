from typing import List
from typing import Optional

from ...configuration import Configuration
from ...core import AssetPair
from ...datastorage import make_datastore
from ...evaluation import get_hourly_data
from ...evaluation import InterpolatingSource
from ...evaluation import make_dataframe_from_json
from ...evaluation import SimulationMarketplace
from ...triggers import BuyTrigger
from ...triggers import make_buy_trigger
from ...triggers import TriggerSpec
from ..ui.simulation import SimulationTab
from .configuration import SingleTriggerEditController
from .configuration import TriggerPaneController


class SimulationTabController:
    def __init__(self, ui: SimulationTab):
        self.ui = ui
        self.spec = TriggerSpec(
            name="Simulated Trigger",
            asset_pair=AssetPair("BTC", "EUR"),
            cooldown_minutes=24 * 3600,
        )
        self.trigger_edit_controller = SingleTriggerEditController(
            self.ui.trigger_pane, self.spec
        )
        self.ui.simulate.clicked.connect(self.simulate)
        self.config: Optional[Configuration] = None

    def set_config(self, config: Configuration):
        self.config = config

    def simulate(self):
        datastore = make_datastore(None)
        trigger_specs = self.trigger_edit_controller.get_config()
        triggers: List[BuyTrigger] = []
        for trigger_spec in trigger_specs:
            asset_pair = trigger_spec.asset_pair
            data = get_hourly_data(asset_pair, self.config.crypto_compare.api_key)
            data = make_dataframe_from_json(data)
            source = InterpolatingSource(data)
            market = SimulationMarketplace(source)
            trigger = make_buy_trigger(datastore, source, market, trigger_spec)
            triggers.append(trigger)
