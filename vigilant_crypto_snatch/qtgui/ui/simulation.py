from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from .altair_widget import WebEngineView
from .configuration import TriggerPane


class SimulationTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.trigger_pane = TriggerPane()
        layout.addWidget(self.trigger_pane)

        simple_plot_view = WebEngineView()
        layout.addWidget(simple_plot_view)
