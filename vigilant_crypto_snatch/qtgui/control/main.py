import datetime
import logging
import time

import coloredlogs

from ... import logger
from ...configuration import Configuration
from ...configuration import YamlConfigurationFactory
from ...watchloop import process_trigger
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

        logger.setLevel("DEBUG")
        self.logger = GuiLogger("DEBUG", self.update_log_message)
        logger.addHandler(self.logger)
        logger.info("Startup complete!")

    def update_config(self, new_config: Configuration):
        self.configuration = new_config
        self.status_tab_controller.config_updated(self.configuration)

    def update_log_message(self, message: str) -> None:
        self.ui.log_message.setText(message)

    def shutdown(self) -> None:
        self.status_tab_controller.shutdown()


class GuiLogger(logging.Handler):
    def __init__(self, level: str, update_message):
        super().__init__(level.upper())
        self.update_message = update_message

    def format(self, record: logging.LogRecord) -> str:
        return f"{datetime.datetime.now().isoformat()} — {record.getMessage()}"

    def emit(self, record: logging.LogRecord) -> None:
        self.update_message(self.format(record))
