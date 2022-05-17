import dataclasses
import json
import sys
from typing import Dict
from typing import Optional

from .. import logger
from ..myrequests import perform_http_request
from ..paths import chat_id_path
from .interface import RemoteLoggerException
from .interface import Sender
from .message_utils import chunk_message


@dataclasses.dataclass()
class TelegramConfig:
    token: str
    level: str
    chat_id: Optional[int] = None

    def to_primitives(self) -> Dict:
        return dict(token=self.token, level=self.level, chat_id=self.chat_id)


class TelegramSender(Sender):
    def __init__(self, config: TelegramConfig):
        self.token = config.token
        if config.chat_id is None:
            self._get_chat_id()
        else:
            self.chat_id = config.chat_id

    def send_message(self, message: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        for chunk in chunk_message(message):
            data = {"chat_id": self.chat_id, "text": chunk}
            j = perform_http_request(url, json=data)
            if not j["ok"]:
                raise RemoteLoggerException(
                    f"Error sending to telegram. Response: `{json.dumps(j)}`"
                )

    def _get_chat_id(self) -> None:
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
