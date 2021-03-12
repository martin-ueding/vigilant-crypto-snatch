import os

import sqlalchemy.orm
import sqlalchemy.ext.declarative


Base = sqlalchemy.ext.declarative.declarative_base()


class Price(Base):
    __tablename__ = 'prices'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    last = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    coin = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    fiat = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __str__(self):
        return f'{self.timestamp}: {self.last} {self.fiat}/{self.coin}'


class Trade(Base):
    __tablename__ = 'trades'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    minutes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    drop = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    volume_coin = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    volume_fiat = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    coin = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    fiat = sqlalchemy.Column(sqlalchemy.String, nullable=False)


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
