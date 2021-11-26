import json
import sys
import threading
from typing import List
from typing import Optional

import requests

from .. import logger
from .message_helper import chunk_message


class TelegramBotException(Exception):
    pass


class TelegramSender(object):
    def __init__(self, token: str, chat_id: int = None):
        self.token = token
        if chat_id is None:
            self.get_chat_id()
        else:
            self.chat_id = chat_id
        self.running = True
        self.queue: List[str] = []
        self.cv = threading.Condition()
        self.thread = threading.Thread(target=self.watch_queue)
        self.thread.start()

    def queue_message(self, message: str) -> None:
        with self.cv:
            if message not in self.queue:
                self.queue.append(message)
            self.cv.notify()

    def has_messages(self) -> bool:
        return len(self.queue) > 0

    def wait_predicate(self) -> bool:
        return self.running or self.has_messages()

    def shutdown(self) -> None:
        logger.debug("Telegram Sender has received shutdown.")
        self.running = False
        with self.cv:
            self.cv.notify()

    def watch_queue(self) -> None:
        while self.running:
            with self.cv:
                while not self.has_messages():
                    self.cv.wait()
                    if not self.running:
                        break

                while self.has_messages():
                    try:
                        message = self.queue[0]
                        self.send_message(message)
                        del self.queue[0]
                    except requests.exceptions.ConnectionError as e:
                        pass

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

    def send_message(self, message: str) -> None:
        logger.debug(f"Sending message to Telegram …")
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        for chunk in chunk_message(message):
            data = {"chat_id": self.chat_id, "text": chunk}
            response = requests.post(url, json=data)
            j = response.json()
            if not j["ok"]:
                raise TelegramBotException(
                    f"Error sending to telegram. Response: `{json.dumps(j)}`"
                )


def make_telegram_sender(config: dict) -> TelegramSender:
    return TelegramSender(
        config["telegram"]["token"], config["telegram"].get("chat_id", None)
    )


def get_sender() -> TelegramSender:
    assert telegram_sender is not None
    return telegram_sender


telegram_sender: Optional[TelegramSender] = None
