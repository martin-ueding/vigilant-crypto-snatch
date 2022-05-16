from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from .configuration import ConfigurationTab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 200)
        self.setWindowTitle("Vigilant Crypto Snatch")
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.configuration_tab = ConfigurationTab()
        self.tab3 = QWidget()
        self.tabs.resize(400, 400)

        # Add tabs
        self.tabs.addTab(self.configuration_tab, "Configuration")
        self.tabs.addTab(self.tab1, "Status")
        self.tabs.addTab(self.tab3, "About")

        layout.addWidget(self.tabs)
