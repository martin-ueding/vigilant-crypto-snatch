class RemoteLoggerException(Exception):
    pass


class Sender:
    def send_message(self, message: str) -> None:
        raise NotImplementedError()  # pragma: no cover
