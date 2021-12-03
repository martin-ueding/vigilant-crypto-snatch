from typing import Optional

from .. import logger
from .interface import Datastore
from .sqlalchemy_store import SqlAlchemyDatastore


def make_datastore(db_path: Optional[str]) -> Datastore:
    path = "/" + db_path if db_path else ""
    logger.debug(f"Trying to open database at `{path}` …")
    return SqlAlchemyDatastore(path)
