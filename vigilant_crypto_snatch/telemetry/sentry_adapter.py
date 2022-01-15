import sentry_sdk

from .. import __version__
from .. import logger
from .interface import TelemetryCollector
from .user_id import get_user_id


class SentryTelemetryCollector(TelemetryCollector):
    def __init__(self):
        logger.debug("Initalizing Sentry …")
        sentry_sdk.init(
            "https://2de30dc7030a4a78a41fad327ba0acff@o1107570.ingest.sentry.io/6134822",
            traces_sample_rate=1.0,
            release=__version__,
        )
        sentry_sdk.set_user(dict(id=get_user_id()))

    def send_event(self, event: str) -> None:
        sentry_sdk.capture_message(event)

    def send_exception(self, exception: Exception) -> None:
        pass