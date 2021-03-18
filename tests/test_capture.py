from vigilant_crypto_snatch import capture


def test_capture() -> None:
    with capture.Capturing() as output:
        print("Hello!")
    assert output == ["Hello!"]
