import os

import sqlalchemy
import sqlalchemy.ext.declarative


Base = sqlalchemy.ext.declarative.declarative_base()


class Price(Base):
    __tablename__ = 'prices'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime)
    last = sqlalchemy.Column(sqlalchemy.Float)

    def __str__(self):
        return '{}: {} EUR/BTC'.format(self.timestamp, self.last)


class Trade(Base):
    __tablename__ = 'trades'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime)
    minutes = sqlalchemy.Column(sqlalchemy.Integer)
    drop = sqlalchemy.Column(sqlalchemy.Integer)
    btc = sqlalchemy.Column(sqlalchemy.Float)
    eur = sqlalchemy.Column(sqlalchemy.Float)


def open_db_session():
    db_path = os.path.expanduser('~/.local/share/vigilant-crypto-snatch/db.sqlite')
    if not os.path.isdir(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    assert os.path.isdir(os.path.dirname(db_path))

    db_url = 'sqlite:///{}'.format(db_path)
    engine = sqlalchemy.create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    return session
