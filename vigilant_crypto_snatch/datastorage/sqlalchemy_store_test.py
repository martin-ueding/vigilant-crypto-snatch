import os
import tempfile

from vigilant_crypto_snatch.datastorage.factory import make_datastore


def test_create_file_db() -> None:
    t = tempfile.NamedTemporaryFile(suffix=".sqlite")
    os.unlink(t.name)
    make_datastore(t.name)
