from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from .configuration import SingleTriggerEdit


class SimulationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trigger Simulation")
        self.resize(1300, 800)

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

        self.summary_table = QTableView()
        left_layout.addWidget(self.summary_table)

        result_toolbox = QGridLayout()
        result_widget = QWidget()
        result_widget.setLayout(result_toolbox)
        splitter.addWidget(result_widget)

        self.close_chart = QChartView()
        result_toolbox.addWidget(self.close_chart, 0, 0)

        self.fear_and_greed_chart = QChartView()
        result_toolbox.addWidget(self.fear_and_greed_chart, 0, 1)

        self.trade_table = QTableView()
        result_toolbox.addWidget(self.trade_table, 1, 0)

        self.gain_chart = QChartView()
        result_toolbox.addWidget(self.gain_chart, 1, 1)

        splitter.setSizes([200, 1000])
