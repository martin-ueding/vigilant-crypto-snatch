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
        self.refresh = QPushButton("Refresh")
        marketplace_group = QGroupBox()
        marketplace_group.setTitle("Marketplace")
        layout = QFormLayout()
        marketplace_group.setLayout(layout)
        layout.addRow("Marketplace:", self.marketplace_name)
        layout.addRow("Balance:", self.balance)
        layout.addRow(self.refresh)

        layout = QVBoxLayout()
        layout.addWidget(marketplace_group)
        self.setLayout(layout)
