from typing import Optional

from . import sqlalchemy_store
from .. import logger
from .interface import Datastore


def make_datastore(db_path: Optional[str]) -> Datastore:
    path = "/" + db_path if db_path else ""
    logger.debug(f"Trying to open database at `{path}` …")
    return sqlalchemy_store.SqlAlchemyDatastore(path)
