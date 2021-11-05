import logging

from . import sender
from .. import configuration
from .. import logger
from .sender import make_telegram_sender
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


def add_telegram_logger(config: dict) -> None:
    if "telegram" in config:
        my_sender = make_telegram_sender(config)
        sender.telegram_sender = my_sender
        telegram_handler = TelegramLogger(
            config["telegram"]["level"], sender.telegram_sender
        )
        logger.addHandler(telegram_handler)

        if "chat_id" not in config["telegram"]:
            config["telegram"]["chat_id"] = sender.telegram_sender.chat_id
            configuration.update_config(config)
