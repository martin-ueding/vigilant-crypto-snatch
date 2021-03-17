import datetime
import logging
import os

import sqlalchemy.orm
import sqlalchemy.ext.declarative


Base = sqlalchemy.ext.declarative.declarative_base()
logger = logging.getLogger("vigilant_crypto_snatch")


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


def garbage_collect_db(
    session: sqlalchemy.orm.Session, cutoff: datetime.datetime
) -> None:
    logger.debug(f"Start cleaning of database before {cutoff} …")

    q = session.query(Price).filter(Price.timestamp < cutoff)
    logger.debug(f"Found {q.count()} old prices, which are going to get deleted.")
    for elem in q:
        session.delete(elem)
    session.commit()
