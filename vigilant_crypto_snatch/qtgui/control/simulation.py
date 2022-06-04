from typing import List

from ...triggers import TriggerSpec
from ..ui.simulation import SimulationTab
from .configuration import TriggerPaneController


class SimulationTabController:
    def __init__(self, ui: SimulationTab):
        self.ui = ui
        self.trigger_edit_controller = TriggerPaneController(self.ui.trigger_pane)

    def populate_triggers(self, trigger_specs: List[TriggerSpec]):
        self.trigger_edit_controller.populate_ui(trigger_specs)
