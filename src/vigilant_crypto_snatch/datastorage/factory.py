from typing import Optional

from . import interface
from . import sqlalchemy_store
from .. import logger


def make_datastore(db_path: Optional[str]) -> interface.Datastore:
    path = "/" + db_path if db_path else ""
    logger.debug(f"Trying to open database at `{path}` …")
    return sqlalchemy_store.SqlAlchemyDatastore(path)
