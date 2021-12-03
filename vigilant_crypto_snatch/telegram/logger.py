import logging
from typing import Optional

from .. import logger
from .sender import TelegramConfig
from .sender import TelegramSender

prefixes = {"CRITICAL": "🔴", "ERROR": "🟠", "WARNING": "🟡", "INFO": "🟢", "DEBUG": "🔵"}


class TelegramLogger(logging.Handler):
    def __init__(self, level: str, sender: TelegramSender):
        super().__init__(level.upper())
        self.sender = sender

    def format(self, record: logging.LogRecord) -> str:
        emoji = prefixes[record.levelname]
        return f"{emoji} {record.getMessage()}"

    def emit(self, record: logging.LogRecord) -> None:
        self.sender.queue_message(self.format(record))


def add_telegram_logger(config: Optional[TelegramConfig]) -> None:
    if config:
        my_sender = TelegramSender(config)
        telegram_sender = my_sender
        telegram_handler = TelegramLogger(config.level, telegram_sender)
        logger.addHandler(telegram_handler)
