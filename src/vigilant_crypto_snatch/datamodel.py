import datetime
import logging
import os

import sqlalchemy.orm
import sqlalchemy.ext.declarative

from . import logger

Base = sqlalchemy.ext.declarative.declarative_base()
user_db_path = os.path.expanduser("~/.local/share/vigilant-crypto-snatch/db.sqlite")


class Price(Base):
    __tablename__ = "prices"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    last = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    coin = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    fiat = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __str__(self):
        return f"{self.timestamp}: {self.last} {self.fiat}/{self.coin}"


class Trade(Base):
    __tablename__ = "trades"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    trigger_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    volume_coin = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    volume_fiat = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    coin = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    fiat = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return (
            f"Trade("
            f"id={repr(self.id)}, "
            f"timestamp={repr(self.timestamp)}, "
            f"trigger_name={repr(self.trigger_name)}, "
            f"volume_coin={repr(self.volume_coin)}, "
            f"volume_fiat={repr(self.volume_fiat)}, "
            f"coin={repr(self.coin)}, "
            f"fiat={repr(self.fiat)}"
            f")"
        )

    def to_dict(self) -> dict:
        return dict(
            timestamp=self.timestamp,
            trigger_name=self.trigger_name,
            volume_coin=self.volume_coin,
            volume_fiat=self.volume_fiat,
            coin=self.coin,
            fiat=self.fiat,
        )


def garbage_collect_db(
    session: sqlalchemy.orm.Session, cutoff: datetime.datetime
) -> None:
    logger.debug(f"Start cleaning of database before {cutoff} …")

    q = session.query(Price).filter(Price.timestamp < cutoff)
    logger.debug(f"Found {q.count()} old prices, which are going to get deleted.")
    for elem in q:
        session.delete(elem)
    session.commit()


def open_db_session(db_path: str) -> sqlalchemy.orm.Session:
    if db_path != "":
        if not os.path.isdir(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))
        assert os.path.isdir(os.path.dirname(db_path))

    db_url = f"sqlite://{db_path}"
    engine = sqlalchemy.create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    return session


def open_memory_db_session() -> sqlalchemy.orm.session:
    return open_db_session("")


def open_user_db_session() -> sqlalchemy.orm.session:
    return open_db_session("/" + user_db_path)
