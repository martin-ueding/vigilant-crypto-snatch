import logging
import sys

import requests


logger = logging.getLogger("vigilant_crypto_snatch")


class TelegramBot(logging.Handler):
    def __init__(self, token: str, level: str, chat_id: None):
        super().__init__(level.upper())
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

    def send_message(self, message: str) -> dict:
        logger.debug("Sending message to Telegram …")
        send_text = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&parse_mode=Markdown&text={message}"
        response = requests.get(send_text)
        return response.json()

    def format(self, record: logging.LogRecord) -> str:
        emoji = prefixes[record.levelname]
        return f"{emoji} {record.getMessage()}"

    def emit(self, record: logging.LogRecord) -> None:
        self.send_message(self.format(record))


prefixes = {"CRITICAL": "🔴", "ERROR": "🟠", "WARNING": "🟡", "INFO": "🟢", "DEBUG": "🔵"}
