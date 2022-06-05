import logging

from ... import logger
from ...configuration import Configuration
from ...configuration import YamlConfigurationFactory
from ..ui.about import AboutTab
from ..ui.configuration import ConfigurationTab
from ..ui.log import LogTab
from ..ui.main import MainWindow
from ..ui.report import ReportTab
from ..ui.simulation import SimulationTab
from .configuration import ConfigurationTabController
from .log import LogTabController
from .report import ReportTabController
from .simulation import SimulationTabController
from .status import StatusTabController


class MainWindowController:
    def __init__(self, ui: MainWindow):
        self.ui = ui
        self.status_tab_controller = StatusTabController(self.ui.status_tab)

        self.simulation_tab = SimulationTab()
        self.simulation_tab_controller = SimulationTabController(self.simulation_tab)
        self.ui.simulate_triggers_action.triggered.connect(self.menu_simulate_triggers)

        self.systray_logger = SystrayLogger("INFO", self.systray_message)
        logger.addHandler(self.systray_logger)

        self.about_window = AboutTab()
        self.ui.about_action.triggered.connect(self.menu_about)

        self.log_messages_window = LogTab()
        self.log_tab_controller = LogTabController(self.log_messages_window)
        self.ui.log_messages_action.triggered.connect(self.menu_log_messages)

        self.configuration_tab = ConfigurationTab()
        self.configuration_tab_controller = ConfigurationTabController(
            self.configuration_tab, self.update_config
        )
        self.ui.settings_action.triggered.connect(self.menu_settings)

        self.report_tab = ReportTab()
        self.report_tab_controller = ReportTabController(self.report_tab)
        self.ui.trade_report_action.triggered.connect(self.menu_trades_report)

        try:
            self.configuration = YamlConfigurationFactory().make_config()
            self.status_tab_controller.config_updated(self.configuration)
            self.simulation_tab_controller.set_config(self.configuration)
        except RuntimeError:
            pass

    def update_config(self, new_config: Configuration):
        self.configuration = new_config
        self.status_tab_controller.config_updated(self.configuration)
        self.simulation_tab_controller.set_config(self.configuration)

    def systray_message(self, message: str, level: str) -> None:
        self.ui.systray.showMessage(level, message)

    def shutdown(self) -> None:
        self.status_tab_controller.shutdown()

    def menu_about(self):
        self.about_window.show()

    def menu_log_messages(self) -> None:
        self.log_messages_window.show()

    def menu_settings(self) -> None:
        self.configuration_tab.show()

    def menu_trades_report(self) -> None:
        self.report_tab.show()

    def menu_simulate_triggers(self) -> None:
        self.simulation_tab.show()


class SystrayLogger(logging.Handler):
    def __init__(self, level: str, update_message):
        super().__init__(level.upper())
        self.update_message = update_message

    def format(self, record: logging.LogRecord) -> str:
        return f"{record.getMessage()}"

    def emit(self, record: logging.LogRecord) -> None:
        self.update_message(self.format(record), record.levelname)
