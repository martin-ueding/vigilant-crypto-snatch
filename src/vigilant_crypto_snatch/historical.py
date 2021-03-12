import datetime

import requests
import sqlalchemy.orm

from . import datamodel
from . import logging


class HistoricalError(RuntimeError):
    pass


def retrieve_historical(then, api_key: str, coin: str, fiat: str):
    """
    If the DB doesn't have the requested data, it requests it from
    Cryptocompare via their API. You have to use your own API key. It's to be
    inserted into the sample_config!!
    """
    timestamp = int(then.timestamp())
    url = f'https://min-api.cryptocompare.com/data/histohour?api_key={api_key}&fsym={coin.upper()}&tsym={fiat.upper()}&limit=1&toTs={timestamp}'

    r = requests.get(url)
    if r.status_code != 200:
        logging.write_log(['The historical API has not returned a success.', 'Status was {}.'.format(r.status_code)])
        raise HistoricalError()

    j = r.json()
    if len(j['Data']) == 0:
        logging.write_log(['There is no payload from the historical API', str(j)])
        raise HistoricalError()

    return j['Data'][-1]['close']


def search_historical(session, timestamp, api_key: str, coin: str, fiat: str):
    """
    Look up the historical price for the drop calculation
    """
    try:
        q = session.query(datamodel.Price).filter(
            datamodel.Price.timestamp < timestamp,
            datamodel.Price.coin == coin,
            datamodel.Price.fiat == fiat,
        ).order_by(datamodel.Price.timestamp.desc())[0]
        if q.timestamp > timestamp - datetime.timedelta(minutes=10):
            return q.last
    except sqlalchemy.orm.exc.NoResultFound:
        pass
    except IndexError:
        pass

    close = retrieve_historical(timestamp, api_key, coin, fiat)

    price = datamodel.Price(timestamp=timestamp, last=close, coin=coin, fiat=fiat)
    session.add(price)
    session.commit()
    return close
