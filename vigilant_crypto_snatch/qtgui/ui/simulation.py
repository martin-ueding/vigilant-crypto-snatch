from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSplitter
from PyQt6.QtWidgets import QTableView
from PyQt6.QtWidgets import QToolBox
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from .altair_widget import WebEngineView
from .configuration import SingleTriggerEdit


class SimulationTab(QWidget):
    def __init__(self):
        super().__init__()

        top_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setLayout(top_layout)
        top_layout.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout()
        left.setLayout(left_layout)
        splitter.addWidget(left)

        self.trigger_pane = SingleTriggerEdit()
        left_layout.addLayout(self.trigger_pane)

        self.simulate = QPushButton("Simulate Trigger")
        left_layout.addWidget(self.simulate)

        self.progress_bar_1 = QProgressBar()
        left_layout.addWidget(self.progress_bar_1)
        self.progress_bar_2 = QProgressBar()
        left_layout.addWidget(self.progress_bar_2)

        result_toolbox = QToolBox()
        splitter.addWidget(result_toolbox)

        self.close_chart = WebEngineView()
        result_toolbox.addItem(self.close_chart, "Close Chart")

        self.fear_and_greed_chart = WebEngineView()
        result_toolbox.addItem(self.fear_and_greed_chart, "Fear &amp; Greed Chart")

        self.trade_table = QTableView()
        result_toolbox.addItem(self.trade_table, "Trade Table")

        self.gain_chart = WebEngineView()
        result_toolbox.addItem(self.gain_chart, "Gain Chart")
