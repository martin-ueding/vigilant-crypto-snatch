import threading
from typing import List
from typing import Optional

from .. import logger
from ..myrequests import HttpRequestError
from .interface import RemoteLoggerException
from .interface import Sender


class MessageQueue(object):
    def __init__(self, sender: Sender):
        self.sender = sender
        self.running = True
        self.queue: List[str] = []
        self.cv = threading.Condition()
        self.thread = threading.Thread(target=self._watch_queue)
        self.thread.start()

    def queue_message(self, message: str) -> None:
        with self.cv:
            if message not in self.queue:
                self.queue.append(message)
            self.cv.notify()

    def _has_messages(self) -> bool:
        return len(self.queue) > 0

    def shutdown(self) -> None:
        logger.debug("Telegram Sender has received shutdown.")
        self.running = False
        with self.cv:
            self.cv.notify()

    def _watch_queue(self) -> None:
        while self.running:
            with self.cv:
                while not self._has_messages():
                    self.cv.wait()
                    if not self.running:
                        break

                while self._has_messages():
                    try:
                        message = self.queue[0]
                        self.sender.send_message(message)
                        del self.queue[0]
                    except RemoteLoggerException:
                        pass
                    except HttpRequestError:
                        pass


class MessageQueueHolder:
    def __init__(self) -> None:
        self._message_queue: Optional[MessageQueue] = None

    def get(self) -> MessageQueue:
        assert self._message_queue
        return self._message_queue

    def set(self, message_queue: MessageQueue) -> None:
        self._message_queue = message_queue


message_queue_holder = MessageQueueHolder()
