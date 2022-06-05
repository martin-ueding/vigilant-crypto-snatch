import pathlib

from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMenuBar
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from .about import AboutTab
from .configuration import ConfigurationTab
from .log import LogTab
from .report import ReportTab
from .simulation import SimulationTab
from .status import StatusTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle("Vigilant Crypto Snatch")

        self.status_tab = StatusTab()
        self.setCentralWidget(self.status_tab)

        icon_path = pathlib.Path(__file__).parent.parent / "logo.png"
        icon = QIcon(str(icon_path))
        self.systray = QSystemTrayIcon(icon, self)
        self.systray.show()
        self.setWindowIcon(icon)

        file_menu = self.menuBar().addMenu("File")
        self.settings_action = QAction("Settings …")
        file_menu.addAction(self.settings_action)

        report_menu = self.menuBar().addMenu("Report")
        self.trade_report_action = QAction("Trade Report …")
        report_menu.addAction(self.trade_report_action)
        simulation_menu = self.menuBar().addMenu("Simulation")
        self.simulate_triggers_action = QAction("Simulate Trigger …")
        simulation_menu.addAction(self.simulate_triggers_action)

        help_menu = self.menuBar().addMenu("Help")
        self.log_messages_action = QAction("Log Messages …")
        help_menu.addAction(self.log_messages_action)
        self.about_action = QAction("About …")
        help_menu.addAction(self.about_action)
