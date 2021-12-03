from .sender import chunk_message
from .sender import split_long_line


def test_chunk_message() -> None:
    message = "12\n45\n67\n90"
    chunks = chunk_message(message, 6)
    assert chunks == ["12\n45", "67\n90"]


def test_split_long_line() -> None:
    message = "123456789"
    chunks = split_long_line(message, 4)
    assert chunks == ["1234", "5678", "9"]
