import datetime
import logging
import os
from typing import *

import sqlalchemy.ext.declarative
import sqlalchemy.orm.exc
from vigilant_crypto_snatch import core

from .. import configuration
from .. import logger
from .interface import Datastore

Base = sqlalchemy.ext.declarative.declarative_base()


class AlchemyPrice(Base):  # type: ignore
    __tablename__ = "prices"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    last = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    coin = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    fiat = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def to_core(self):
        return core.Price(
            timestamp=self.timestamp,
            last=self.last,
            coin=self.coin,
            fiat=self.fiat,
        )


def price_to_alchemy_price(price: core.Price) -> AlchemyPrice:
    return AlchemyPrice(
        timestamp=price.timestamp,
        last=price.last,
        coin=price.coin,
        fiat=price.fiat,
    )


class AlchemyTrade(Base):  # type: ignore
    __tablename__ = "trades"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    trigger_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    volume_coin = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    volume_fiat = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    coin = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    fiat = sqlalchemy.Column(sqlalchemy.String, nullable=False)


def trade_to_alchemy_trade(trade: core.Trade) -> AlchemyTrade:
    return AlchemyTrade(
        timestamp=trade.timestamp,
        trigger_name=trade.trigger_name,
        volume_coin=trade.volume_coin,
        volume_fiat=trade.volume_fiat,
        coin=trade.coin,
        fiat=trade.fiat,
    )


class SqlAlchemyDatastore(Datastore):
    def __init__(self, db_path: str):
        if db_path != "":
            if not os.path.isdir(os.path.dirname(db_path)):
                os.makedirs(os.path.dirname(db_path))
            assert os.path.isdir(os.path.dirname(db_path))

        db_url = f"sqlite://{db_path}"
        engine = sqlalchemy.create_engine(db_url)
        Base.metadata.create_all(engine)
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        self.session = Session()  # type: ignore

    def add_price(self, price: core.Price) -> None:
        alchemy_price = price_to_alchemy_price(price)
        self.session.add(alchemy_price)
        self.session.commit()

    def add_trade(self, trade: core.Trade) -> None:
        alchemy_trade = trade_to_alchemy_trade(trade)
        self.session.add(alchemy_trade)
        self.session.commit()

    def get_price_around(
        self,
        then: datetime.datetime,
        coin: str,
        fiat: str,
        tolerance: datetime.timedelta,
    ) -> Optional[core.Price]:
        try:
            q = (
                self.session.query(AlchemyPrice)
                .filter(
                    AlchemyPrice.timestamp < then,
                    AlchemyPrice.coin == coin,
                    AlchemyPrice.fiat == fiat,
                )
                .order_by(AlchemyPrice.timestamp.desc())[0]
            )
            if q.timestamp > then - tolerance:
                logger.debug(
                    f"Found historical price for {then} in database: {q.last} {fiat}/{coin}."
                )
                return q.to_core()
        except sqlalchemy.orm.exc.NoResultFound:
            pass
        except IndexError:
            pass

        return None

    def was_triggered_since(
        self, trigger_name: str, coin: str, fiat: str, then: datetime.datetime
    ) -> bool:
        trade_count = (
            self.session.query(AlchemyTrade)
            .filter(
                AlchemyTrade.trigger_name == trigger_name,
                AlchemyTrade.timestamp > then,
                AlchemyTrade.coin == coin,
                AlchemyTrade.fiat == fiat,
            )
            .count()
        )
        return trade_count != 0

    def get_all_trades(self) -> List[core.Trade]:
        pass

    def clean_old(self, cutoff: datetime.datetime):
        logger.debug(f"Start cleaning of database before {cutoff} …")

        q = self.session.query(AlchemyPrice).filter(AlchemyPrice.timestamp < cutoff)
        logger.debug(f"Found {q.count()} old prices, which are going to get deleted.")
        for elem in q:
            self.session.delete(elem)
        self.session.commit()
