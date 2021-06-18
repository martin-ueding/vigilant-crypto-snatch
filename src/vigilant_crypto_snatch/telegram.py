import logging
import sys
import typing
import json

import requests

from . import configuration
from . import logger


prefixes = {"CRITICAL": "🔴", "ERROR": "🟠", "WARNING": "🟡", "INFO": "🟢", "DEBUG": "🔵"}


class TelegramBotException(Exception):
    pass


class TelegramLogger(logging.Handler):
    def __init__(self, token: str, level: str, chat_id: int = None):
        super().__init__(level.upper())
        self.sender = TelegramSender(token, chat_id)

    def format(self, record: logging.LogRecord) -> str:
        emoji = prefixes[record.levelname]
        return f"{emoji} {record.getMessage()}"

    def emit(self, record: logging.LogRecord) -> None:
        self.sender.send_message(self.format(record))


class TelegramSender(object):
    def __init__(self, token: str, chat_id: int = None):
        self.token = token
        if chat_id is None:
            self.get_chat_id()
        else:
            self.chat_id = chat_id

    def get_chat_id(self) -> None:
        response = requests.get(f"https://api.telegram.org/bot{self.token}/getUpdates")
        response.raise_for_status()
        data = response.json()
        result = data["result"]
        if len(result) == 0:
            logger.critical(
                f"Telegram bot has no chats. Did you write it a message? Response was: {data}."
            )
            sys.exit(1)
        self.chat_id = int(data["result"][-1]["message"]["chat"]["id"])
        logger.info(f"Your Telegram chat ID is {self.chat_id}.")

    def send_message(self, message: str) -> typing.Optional[dict]:
        logger.debug(f"Sending message to Telegram …")
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        for chunk in chunk_message(message):
            data = {"chat_id": self.chat_id, "text": chunk}
            try:
                response = requests.post(url, json=data)
                j = response.json()
                if not j["ok"]:
                    raise TelegramBotException(
                        f"Error sending to telegram. Response: `{json.dumps(j)}`"
                    )
            except requests.exceptions.ConnectionError as e:
                pass


def add_telegram_logger() -> None:
    config = configuration.load_config()
    if "telegram" in config:
        telegram_handler = TelegramLogger(
            config["telegram"]["token"],
            config["telegram"]["level"],
            config["telegram"].get("chat_id", None),
        )
        logger.addHandler(telegram_handler)

        if not "chat_id" in config["telegram"]:
            config["telegram"]["chat_id"] = telegram_handler.chat_id
            configuration.update_config(config)


def chunk_message(message: str, char_limit: int = 4000) -> typing.List[str]:
    lines = message.split("\n")
    capped_lines = []
    for line in lines:
        if len(line) < char_limit:
            capped_lines.append(line)
        else:
            lines += split_long_line(line, char_limit)
    chunks = []
    current_chunk = []
    current_size = 0
    for line in capped_lines:
        if len(line) + current_size >= char_limit:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_size = 0
        current_chunk.append(line)
        current_size += len(line) + 1
    if len(current_chunk) > 0:
        chunks.append("\n".join(current_chunk))
    return chunks


def split_long_line(line: str, char_limit: int = 4000) -> typing.List[str]:
    intervals = len(line) // char_limit + 1
    chunks = [line[(i * char_limit) : ((i + 1) * char_limit)] for i in range(intervals)]
    return chunks
