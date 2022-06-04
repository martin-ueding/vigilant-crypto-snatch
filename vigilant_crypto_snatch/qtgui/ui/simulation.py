from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from .altair_widget import WebEngineView
from .configuration import SingleTriggerEdit
from .configuration import TriggerEditWindow
from .configuration import TriggerPane


class SimulationTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.trigger_pane = SingleTriggerEdit()
        layout.addLayout(self.trigger_pane)

        self.simulate = QPushButton("Simulate Trigger")
        layout.addWidget(self.simulate)

        simple_plot_view = WebEngineView()
        layout.addWidget(simple_plot_view)
