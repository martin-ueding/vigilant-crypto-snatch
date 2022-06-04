import pathlib

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from .about import AboutTab
from .configuration import ConfigurationTab
from .log import LogTab
from .report import ReportTab
from .simulation import SimulationTab
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
        self.report_tab = ReportTab()
        self.log_tab = LogTab()
        self.simulation_tab = SimulationTab()
        self.tabs.addTab(self.status_tab, "Status")
        self.tabs.addTab(self.report_tab, "Report")
        self.tabs.addTab(self.configuration_tab, "Configuration")
        self.tabs.addTab(self.simulation_tab, "Simulation")
        self.tabs.addTab(self.log_tab, "Log Messages")
        self.tabs.addTab(self.about_tab, "About")

        icon_path = pathlib.Path(__file__).parent.parent / "logo.png"
        icon = QIcon(str(icon_path))
        self.systray = QSystemTrayIcon(icon, self)
        self.systray.show()
        self.setWindowIcon(icon)
