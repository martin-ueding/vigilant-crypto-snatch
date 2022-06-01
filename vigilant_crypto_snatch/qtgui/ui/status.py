from typing import Dict

from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QFormLayout
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QTableView
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


class StatusTab(QWidget):
    def __init__(self):
        super().__init__()

        self.balance = QTableView()
        self.prices = QTableView()
        self.active_triggers = QTableView()
        self.watch_triggers = QCheckBox()

        marketplace_group = QGroupBox()
        marketplace_group.setTitle("Marketplace")
        layout = QHBoxLayout()
        marketplace_group.setLayout(layout)

        balance_group = QGroupBox()
        balance_group.setTitle("Balances")
        balance_group_layout = QVBoxLayout()
        balance_group.setLayout(balance_group_layout)
        balance_group_layout.addWidget(self.balance)
        layout.addWidget(balance_group)

        prices_group = QGroupBox()
        prices_group.setTitle("Spot Prices")
        prices_group_layout = QVBoxLayout()
        prices_group.setLayout(prices_group_layout)
        prices_group_layout.addWidget(self.prices)
        layout.addWidget(prices_group)

        trigger_group = QGroupBox()
        trigger_group.setTitle("Triggers")
        layout = QFormLayout()
        trigger_group.setLayout(layout)
        layout.addRow(self.active_triggers)
        layout.addRow("Watch triggers:", self.watch_triggers)

        layout = QVBoxLayout()
        layout.addWidget(marketplace_group)
        layout.addWidget(trigger_group)
        self.setLayout(layout)
