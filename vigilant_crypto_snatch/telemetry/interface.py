import dataclasses


@dataclasses.dataclass()
class TelemetryConfig:
    collect: bool = False


class TelemetryCollector:
    def send_event(self, event: str) -> None:
        raise NotImplementedError()  # pragma: no cover

    def send_exception(self, exception: Exception) -> None:
        raise NotImplementedError()  # pragma: no cover

    def send_session(self, name: str) -> None:
        raise NotImplementedError()  # pragma: no cover


class NullTelemetryCollector(TelemetryCollector):
    def send_event(self, event: str) -> None:
        pass

    def send_exception(self, exception: Exception) -> None:
        pass

    def send_session(self, name: str) -> None:
        pass
