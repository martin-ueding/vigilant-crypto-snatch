import datetime
import os
from typing import *

import sqlalchemy.ext.declarative
import sqlalchemy.orm.exc

from .. import core
from .. import logger
from .interface import Datastore
from .interface import DatastoreException

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

    def to_core(self):
        return core.Trade(
            timestamp=self.timestamp,
            trigger_name=self.trigger_name,
            volume_coin=self.volume_coin,
            volume_fiat=self.volume_fiat,
            coin=self.coin,
            fiat=self.fiat,
        )


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
    def __init__(self, db_path: str = ""):
        if db_path != "":
            if not os.path.isdir(os.path.dirname(db_path)):
                os.makedirs(os.path.dirname(db_path))
            assert os.path.isdir(os.path.dirname(db_path))

        db_url = f"sqlite://{db_path}"
        try:
            engine = sqlalchemy.create_engine(db_url)
            Base.metadata.create_all(engine)
            Session = sqlalchemy.orm.sessionmaker(bind=engine)
            self.session = Session()  # type: ignore
        except sqlalchemy.exc.OperationalError as e:
            raise DatastoreException(
                f"Something went wrong with the database. Perhaps it is easiest to just delete the database file."
            ) from e

    def add_price(self, price: core.Price) -> None:
        alchemy_price = price_to_alchemy_price(price)

        try:
            self.session.add(alchemy_price)
            self.session.commit()
        except sqlalchemy.exc.OperationalError as e:
            raise DatastoreException(
                f"Something went wrong with the database. Perhaps it is easiest to just delete the database file."
            ) from e

    def add_trade(self, trade: core.Trade) -> None:
        alchemy_trade = trade_to_alchemy_trade(trade)

        try:
            self.session.add(alchemy_trade)
            self.session.commit()
        except sqlalchemy.exc.OperationalError as e:
            raise DatastoreException(
                f"Something went wrong with the database. Perhaps it is easiest to just delete the database file."
            ) from e

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
                    AlchemyPrice.timestamp <= then,
                    AlchemyPrice.coin == coin,
                    AlchemyPrice.fiat == fiat,
                )
                .order_by(AlchemyPrice.timestamp.desc())[0]
            )
            if q.timestamp >= then - tolerance:
                logger.debug(
                    f"Found historical price for {then} in database: {q.last} {fiat}/{coin}."
                )
                return q.to_core()
        except sqlalchemy.orm.exc.NoResultFound:
            pass
        except IndexError:
            pass
        except sqlalchemy.exc.OperationalError as e:
            raise DatastoreException(
                f"Something went wrong with the database. Perhaps it is easiest to just delete the database file."
            ) from e

        return None

    def was_triggered_since(
        self, trigger_name: str, coin: str, fiat: str, then: datetime.datetime
    ) -> bool:
        try:
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
        except sqlalchemy.exc.OperationalError as e:
            raise DatastoreException(
                f"Something went wrong with the database. Perhaps it is easiest to just delete the database file."
            ) from e

    def get_all_trades(self) -> List[core.Trade]:
        q = self.session.query(AlchemyTrade)
        result = [elem.to_core() for elem in q]
        return result

    def get_all_prices(self) -> List[core.Price]:
        q = self.session.query(AlchemyPrice)
        result = [elem.to_core() for elem in q]
        return result

    def clean_old(self, cutoff: datetime.datetime):
        logger.debug(f"Start cleaning of database before {cutoff} …")

        try:
            q = self.session.query(AlchemyPrice).filter(AlchemyPrice.timestamp < cutoff)
            logger.debug(
                f"Found {q.count()} old prices, which are going to get deleted."
            )
            for elem in q:
                self.session.delete(elem)
            self.session.commit()
        except sqlalchemy.exc.OperationalError as e:
            raise DatastoreException(
                f"Something went wrong with the database. Perhaps it is easiest to just delete the database file."
            ) from e