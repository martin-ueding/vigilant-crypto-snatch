from ...configuration import Configuration
from ...configuration import YamlConfigurationFactory
from ..ui.main import MainWindow
from .configuration import ConfigurationTabController
from .status import StatusTabController


class MainWindowController:
    def __init__(self, ui: MainWindow):
        self.ui = ui
        self.configuration = YamlConfigurationFactory().make_config()
        self.configuration_tab_controller = ConfigurationTabController(
            self.ui.configuration_tab, self.update_config
        )
        self.status_tab_controller = StatusTabController(self.ui.status_tab)
        self.status_tab_controller.config_updated(self.configuration)

    def update_config(self, new_config: Configuration):
        self.configuration = new_config
        self.status_tab_controller.config_updated(self.configuration)
