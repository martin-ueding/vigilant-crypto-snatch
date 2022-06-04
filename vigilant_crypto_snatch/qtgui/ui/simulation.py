from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QTableView
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from .altair_widget import WebEngineView
from .configuration import SingleTriggerEdit


class SimulationTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.trigger_pane = SingleTriggerEdit()
        layout.addLayout(self.trigger_pane)

        self.simulate = QPushButton("Simulate Trigger")
        layout.addWidget(self.simulate)

        self.progress_bar = QProgressBar()
        # layout.addWidget(self.progress_bar)

        self.trade_table = QTableView()
        # layout.addWidget(self.trade_table)

        self.gain_chart = WebEngineView()
        layout.addWidget(self.gain_chart)
