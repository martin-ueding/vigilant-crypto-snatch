from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class StatusTab(QWidget):
    def __init__(self):
        super().__init__()

        self.balance = QTableView()
        self.prices = QTableView()
        self.active_triggers = QTableView()
        self.watch_triggers = QCheckBox()

        marketplace_layout = QHBoxLayout()

        balance_group = QGroupBox()
        balance_group.setTitle("Balances")
        balance_group_layout = QVBoxLayout()
        balance_group.setLayout(balance_group_layout)
        balance_group_layout.addWidget(self.balance)
        marketplace_layout.addWidget(balance_group)

        prices_group = QGroupBox()
        prices_group.setTitle("Spot Prices")
        prices_group_layout = QVBoxLayout()
        prices_group.setLayout(prices_group_layout)
        prices_group_layout.addWidget(self.prices)
        marketplace_layout.addWidget(prices_group)

        trigger_group = QGroupBox()
        trigger_group.setTitle("Triggers")
        layout = QFormLayout()
        trigger_group.setLayout(layout)
        layout.addRow(self.active_triggers)
        layout.addRow("Execute triggers:", self.watch_triggers)

        layout = QVBoxLayout()
        layout.addLayout(marketplace_layout)
        layout.addWidget(trigger_group)
        self.setLayout(layout)
