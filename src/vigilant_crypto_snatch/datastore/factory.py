from . import interface
from . import sqlalchemy_store


def make_datastore(path: str) -> interface.Datastore:
    return sqlalchemy_store.SqlAlchemyDatastore(path)
