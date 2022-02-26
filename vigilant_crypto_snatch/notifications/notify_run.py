import dataclasses

from ..myrequests import perform_post_request
from .interface import Sender


@dataclasses.dataclass()
class NotifyRunConfig:
    channel: str
    level: str = "info"


class NotifyRunSender(Sender):
    def __init__(self, config: NotifyRunConfig):
        self.channel = config.channel

    def send_message(self, message: str) -> None:
        perform_post_request(f"https://notify.run/{self.channel}", message.encode())
