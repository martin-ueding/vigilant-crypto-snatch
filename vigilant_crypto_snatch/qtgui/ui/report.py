from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class ReportTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.update_report = QPushButton("Update Report")
        layout.addWidget(self.update_report)

        tabs = QTabWidget()

        all_trades_tab = QWidget()
        all_trades_layout = QVBoxLayout()
        self.all_trades = QTableView()
        all_trades_layout.addWidget(self.all_trades)
        all_trades_tab.setLayout(all_trades_layout)
        tabs.addTab(all_trades_tab, "All Trades")

        pairs_tab = QWidget()
        pairs_layout = QVBoxLayout()
        self.pairs_table = QTableView()
        pairs_layout.addWidget(self.pairs_table)
        pairs_tab.setLayout(pairs_layout)
        tabs.addTab(pairs_tab, "Per Currency Pair")

        pairs_triggers_tab = QWidget()
        pairs_triggers_layout = QVBoxLayout()
        self.pairs_triggers_table = QTableView()
        pairs_triggers_layout.addWidget(self.pairs_triggers_table)
        pairs_triggers_tab.setLayout(pairs_triggers_layout)
        tabs.addTab(pairs_triggers_tab, "Per Currency Pair and Trigger")

        layout.addWidget(tabs)

        self.setLayout(layout)
