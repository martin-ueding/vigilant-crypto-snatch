import datetime


class FearAndGreedIndex:
    def get_value(self, now: datetime.datetime) -> int:
        raise NotImplementedError()  # pragma: no cover


class FearAndGreedException(Exception):
    pass
