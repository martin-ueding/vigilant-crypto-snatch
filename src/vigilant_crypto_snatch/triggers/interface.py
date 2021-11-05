import datetime


class Trigger(object):
    def get_name(self) -> str:
        raise NotImplementedError()

    def fire(self, now: datetime.datetime) -> None:
        raise NotImplementedError()

    def has_cooled_off(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()

    def is_triggered(self, now: datetime.datetime) -> bool:
        raise NotImplementedError()
