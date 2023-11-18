import time

from .interface import Sender
from .message_queue import MessageQueue


class MockSender(Sender):
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send_message(self, message: str) -> None:
        self.messages.append(message)


def test_sending() -> None:
    mock_sender = MockSender()
    message_queue = MessageQueue(mock_sender)
    assert mock_sender.messages == []
    message_queue.queue_message("Test")
    while len(mock_sender.messages) == 0:
        time.sleep(0.001)
    assert mock_sender.messages == ["Test"]
    message_queue.shutdown()
