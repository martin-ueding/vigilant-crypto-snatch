from . import interface
from . import sqlalchemy_store
from .. import configuration
from .. import logger


def make_datastore(persistent: bool) -> interface.Datastore:
    path = "/" + configuration.user_db_path if persistent else ""
    logger.debug(f"Trying to open database at `{path}` …")
    return sqlalchemy_store.SqlAlchemyDatastore(path)
