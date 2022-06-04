import datetime
import logging

from ... import logger
from ..ui.log import LogTab


class LogTabController:
    def __init__(self, ui: LogTab):
        self.ui = ui
        self.ui.log_level.currentTextChanged.connect(self.log_level_changed)
        self.ui.clear.clicked.connect(self.clear)

        logger.setLevel("DEBUG")
        self.logger = GuiLogger("DEBUG", self.add_message)
        logger.addHandler(self.logger)

    def add_message(self, message: str, level: str) -> None:
        self.ui.text_edit.append(message)

    def log_level_changed(self, new_level: str) -> None:
        self.logger.setLevel(new_level.upper())

    def clear(self) -> None:
        self.ui.text_edit.setText("")


class GuiLogger(logging.Handler):
    def __init__(self, level: str, update_message):
        super().__init__(level.upper())
        self.update_message = update_message

    def format(self, record: logging.LogRecord) -> str:
        return f"[{datetime.datetime.now().isoformat()} {record.levelname}] {record.getMessage()}"

    def emit(self, record: logging.LogRecord) -> None:
        self.update_message(self.format(record), record.levelname)
