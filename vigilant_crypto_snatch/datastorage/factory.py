import pathlib
from typing import Optional

from .. import logger
from .interface import Datastore
from .sqlalchemy_store import SqlAlchemyDatastore


def make_datastore(path: Optional[pathlib.Path]) -> Datastore:
    logger.debug(f"Trying to open database at `{path}` …")
    return SqlAlchemyDatastore(path)
