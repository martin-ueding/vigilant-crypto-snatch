import datetime


class FearAndGreedIndex:
    def get_value(self, now: datetime.datetime) -> int:
        raise NotImplementedError()


class FearAndGreedException(Exception):
    pass
