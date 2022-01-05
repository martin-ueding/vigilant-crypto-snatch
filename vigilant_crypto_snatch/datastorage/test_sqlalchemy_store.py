import os
import pathlib
import tempfile

from .factory import make_datastore


def test_create_file_db() -> None:
    t = tempfile.NamedTemporaryFile(suffix=".sqlite")
    os.unlink(t.name)
    make_datastore(pathlib.Path(t.name))
