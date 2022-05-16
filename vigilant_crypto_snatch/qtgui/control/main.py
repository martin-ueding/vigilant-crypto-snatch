from ..ui.main import MainWindow
from .configuration import ConfigurationTabController


class MainWindowController:
    def __init__(self, main_window: MainWindow):
        self.main_window = main_window
        self.configuration_tab_controller = ConfigurationTabController(
            self.main_window.configuration_tab
        )
