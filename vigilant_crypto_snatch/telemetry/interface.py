import dataclasses


@dataclasses.dataclass()
class TelemetryConfig:
    collect: bool


class TelemetryCollector:
    def send_event(self, event: str) -> None:
        raise NotImplementedError()  # pragma: no cover

    def send_exception(self, exception: Exception) -> None:
        raise NotImplementedError()  # pragma: no cover
