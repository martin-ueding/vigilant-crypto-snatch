import logging

from .message_queue import MessageQueue

prefixes = {"CRITICAL": "🔴", "ERROR": "🟠", "WARNING": "🟡", "INFO": "🟢", "DEBUG": "🔵"}


class RemoteLogger(logging.Handler):
    def __init__(self, level: str, sender: MessageQueue):
        super().__init__(level.upper())
        self.sender = sender

    def format(self, record: logging.LogRecord) -> str:
        emoji = prefixes[record.levelname]
        return f"{emoji} {record.getMessage()}"

    def emit(self, record: logging.LogRecord) -> None:
        self.sender.queue_message(self.format(record))
