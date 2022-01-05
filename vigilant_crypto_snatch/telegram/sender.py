import dataclasses
import json
import sys
import threading
from typing import List
from typing import Optional

from .. import logger
from ..myrequests import HttpRequestError
from ..myrequests import perform_http_request
from ..paths import chat_id_path


@dataclasses.dataclass()
class TelegramConfig:
    token: str
    level: str
    chat_id: Optional[int] = None


class TelegramBotException(Exception):
    pass


class TelegramSender(object):
    def __init__(self, config: TelegramConfig):
        self.token = config.token
        if config.chat_id is None:
            self.get_chat_id()
        else:
            self.chat_id = config.chat_id
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
                    except TelegramBotException:
                        pass
                    except HttpRequestError:
                        pass

    def get_chat_id(self) -> None:
        if chat_id_path.exists():
            with open(chat_id_path) as f:
                self.chat_id = json.load(f)
                return
        data = perform_http_request(
            f"https://api.telegram.org/bot{self.token}/getUpdates"
        )
        result = data["result"]
        if len(result) == 0:
            logger.critical(
                f"Telegram bot has no chats. Did you write it a message? Response was: {data}."
            )
            sys.exit(1)
        self.chat_id = int(data["result"][-1]["message"]["chat"]["id"])
        with open(chat_id_path, "w") as f:
            json.dump(self.chat_id, f)
        logger.info(f"Your Telegram chat ID is {self.chat_id}.")

    def send_message(self, message: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        for chunk in chunk_message(message):
            data = {"chat_id": self.chat_id, "text": chunk}
            j = perform_http_request(url, json=data)
            if not j["ok"]:
                raise TelegramBotException(
                    f"Error sending to telegram. Response: `{json.dumps(j)}`"
                )


class TelegramSenderHolder:
    def __init__(self):
        self._telegram_sender: Optional[TelegramSender] = None

    def get_sender(self) -> TelegramSender:
        assert self._telegram_sender
        return self._telegram_sender

    def set_sender(self, telegram_sender: TelegramSender) -> None:
        self._telegram_sender = telegram_sender


telegram_sender_holder = TelegramSenderHolder()


def chunk_message(message: str, char_limit: int = 4000) -> List[str]:
    lines = message.split("\n")
    capped_lines = []
    for line in lines:
        if len(line) < char_limit:
            capped_lines.append(line)
        else:
            lines += split_long_line(line, char_limit)
    chunks = []
    current_chunk: List[str] = []
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


def split_long_line(line: str, char_limit: int = 4000) -> List[str]:
    intervals = len(line) // char_limit + 1
    chunks = [line[(i * char_limit) : ((i + 1) * char_limit)] for i in range(intervals)]
    return chunks
