import datetime


class Trigger(object):
    def get_name(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    def fire(self, now: datetime.datetime) -> None:
        raise NotImplementedError()  # pragma: no cover

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()  # pragma: no cover

    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()  # pragma: no cover
