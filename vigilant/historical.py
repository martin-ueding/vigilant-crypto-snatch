import datetime

import requests
import sqlalchemy.orm

import vigilant.datamodel
import vigilant.logging


class HistoricalError(RuntimeError):
    pass


def retrieve_historical(then, api_key):
    """
    If the DB doesn't have the requested data, it requests it from
    Cryptocompare via their API. You have to use your own API key. It's to be
    inserted into the sample_config!!
    """
    timestamp = int(then.timestamp())
    url = 'https://min-api.cryptocompare.com/data/histohour?api_key={}&fsym=BTC&tsym=EUR&limit=1&toTs={}'.format(
        api_key,
        timestamp)

    r = requests.get(url)
    if r.status_code != 200:
        vigilant.logging.write_log(['The historical API has not returned a success.', 'Status was {}.'.format(r.status_code)])
        raise HistoricalError()

    j = r.json()
    if len(j['Data']) == 0:
        vigilant.logging.write_log(['There is no payload from the historical API', str(j)])
        raise HistoricalError()

    return j['Data'][-1]['close']


def search_historical(session, timestamp, api_key):
    """
    Look up the historical price for the drop calculation
    """
    try:
        q = session.query(vigilant.datamodel.Price).filter(vigilant.datamodel.Price.timestamp < timestamp).order_by(vigilant.datamodel.Price.timestamp.desc())[0]
        if q.timestamp > timestamp - datetime.timedelta(minutes=10):
            return q.last
    except sqlalchemy.orm.exc.NoResultFound:
        pass
    except IndexError:
        pass

    close = retrieve_historical(timestamp, api_key)

    price = vigilant.datamodel.Price(timestamp=timestamp, last=close)
    session.add(price)
    session.commit()
    return close
