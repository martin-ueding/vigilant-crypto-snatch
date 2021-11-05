from typing import Optional

from . import interface
from . import sqlalchemy_store
from .. import configuration


def make_datastore(persistent: bool) -> interface.Datastore:
    path = configuration.user_db_path if persistent else ""
    return sqlalchemy_store.SqlAlchemyDatastore(path)
