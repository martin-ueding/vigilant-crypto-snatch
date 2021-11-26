import os
import tempfile

from vigilant_crypto_snatch.datastorage.sqlalchemy_store import SqlAlchemyDatastore


def test_create_file_db() -> None:
    t = tempfile.NamedTemporaryFile(suffix=".sqlite")
    os.unlink(t.name)
    datastore = SqlAlchemyDatastore(f"/{t.name}")
