import logging

from ... import logger
from ...configuration import Configuration
from ...configuration import YamlConfigurationFactory
from ..ui.main import MainWindow
from .configuration import ConfigurationTabController
from .log import LogTabController
from .report import ReportTabController
from .simulation import SimulationTabController
from .status import StatusTabController


class MainWindowController:
    def __init__(self, ui: MainWindow):
        self.ui = ui
        self.status_tab_controller = StatusTabController(self.ui.status_tab)
        self.configuration_tab_controller = ConfigurationTabController(
            self.ui.configuration_tab, self.update_config
        )
        self.report_tab_controller = ReportTabController(self.ui.report_tab)
        self.log_tab_controller = LogTabController(self.ui.log_tab)
        self.simulation_tab_controller = SimulationTabController(self.ui.simulation_tab)

        try:
            self.configuration = YamlConfigurationFactory().make_config()
            self.status_tab_controller.config_updated(self.configuration)
            self.simulation_tab_controller.populate_triggers(
                self.configuration.triggers
            )
        except RuntimeError:
            pass

        self.systray_logger = SystrayLogger("INFO", self.systray_message)
        logger.addHandler(self.systray_logger)

    def update_config(self, new_config: Configuration):
        self.configuration = new_config
        self.status_tab_controller.config_updated(self.configuration)

    def update_log_message(self, message: str, level: str) -> None:
        self.ui.log_message.setText(message)

    def systray_message(self, message: str, level: str) -> None:
        self.ui.systray.showMessage(level, message)

    def shutdown(self) -> None:
        self.status_tab_controller.shutdown()


class SystrayLogger(logging.Handler):
    def __init__(self, level: str, update_message):
        super().__init__(level.upper())
        self.update_message = update_message

    def format(self, record: logging.LogRecord) -> str:
        return f"{record.getMessage()}"

    def emit(self, record: logging.LogRecord) -> None:
        self.update_message(self.format(record), record.levelname)
