from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from .about import AboutTab
from .configuration import ConfigurationTab
from .status import StatusTab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle("Vigilant Crypto Snatch")

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.configuration_tab = ConfigurationTab()
        self.about_tab = AboutTab()
        self.status_tab = StatusTab()
        self.tabs.addTab(self.status_tab, "Status")
        self.tabs.addTab(self.configuration_tab, "Configuration")
        self.tabs.addTab(self.about_tab, "About")

        self.log_message = QLabel("Log")
        layout.addWidget(self.log_message)
