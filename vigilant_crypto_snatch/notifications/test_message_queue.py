from typing import List

from .interface import Sender
from .message_queue import MessageQueue


class MockSender(Sender):
    def __init__(self):
        self.messages: List[str] = []

    def send_message(self, message: str) -> None:
        self.messages.append(message)
