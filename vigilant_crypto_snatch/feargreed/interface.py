import datetime


class FearAndGreedIndex:
    def get_value(self, now: datetime.date, today: datetime.date) -> int:
        raise NotImplementedError()  # pragma: no cover


class FearAndGreedException(Exception):
    pass
