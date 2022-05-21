from typing import Dict

from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QFormLayout
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


class StatusTab(QWidget):
    def __init__(self):
        super().__init__()

        self.marketplace_name = QLabel()
        self.balance = QLabel()
        self.last_refresh = QLabel()
        self.prices = QLabel()
        self.active_triggers = QLabel()
        self.watch_triggers = QCheckBox()
        self.refresh = QPushButton("Refresh")

        marketplace_group = QGroupBox()
        marketplace_group.setTitle("Marketplace")
        layout = QFormLayout()
        marketplace_group.setLayout(layout)
        layout.addRow("Provider:", self.marketplace_name)
        layout.addRow("Balance:", self.balance)
        layout.addRow("Spot prices:", self.prices)
        layout.addRow("Last refresh:", self.last_refresh)
        layout.addRow(self.refresh)

        trigger_group = QGroupBox()
        trigger_group.setTitle("Triggers")
        layout = QFormLayout()
        trigger_group.setLayout(layout)
        layout.addRow("Active triggers:", self.active_triggers)
        layout.addRow("Watch triggers:", self.watch_triggers)

        layout = QVBoxLayout()
        layout.addWidget(marketplace_group)
        layout.addWidget(trigger_group)
        self.setLayout(layout)
