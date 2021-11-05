import datetime
import logging
import os
from typing import List

import sqlalchemy.ext.declarative
import sqlalchemy.orm
from vigilant_crypto_snatch import core
from vigilant_crypto_snatch import triggers

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
    def add_price(self, price: core.Price) -> None:
        alchemy_price = price_to_alchemy_price(price)
        self.session.add(alchemy_price)
        self.session.commit()

    def add_trade(self, trade: core.Trade) -> None:
        alchemy_trade = trade_to_alchemy_trade(trade)
        self.session.add(alchemy_trade)
        self.session.commit()

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

    def get_price_around(
        self, then: datetime.datetime, tolerance: datetime.timedelta
    ) -> core.Price:
        pass

    def was_triggered_since(
        self, trigger: triggers.BuyTrigger, then: datetime.datetime
    ) -> bool:
        trade_count = (
            self.session.query(AlchemyTrade)
            .filter(
                AlchemyTrade.trigger_name == trigger.get_name(),
                AlchemyTrade.timestamp > then,
                AlchemyTrade.coin == trigger.coin,
                AlchemyTrade.fiat == trigger.fiat,
            )
            .count()
        )
        return trade_count == 0

    def get_all_trades(self) -> List[core.Price]:
        pass

    def clean_old(self, cutoff: datetime.datetime):
        logger.debug(f"Start cleaning of database before {cutoff} …")

        q = self.session.query(AlchemyPrice).filter(AlchemyPrice.timestamp < cutoff)
        logger.debug(f"Found {q.count()} old prices, which are going to get deleted.")
        for elem in q:
            self.session.delete(elem)
        self.session.commit()
