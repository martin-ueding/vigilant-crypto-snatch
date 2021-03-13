import datetime
import logging

import requests
import sqlalchemy.orm

from . import datamodel
from . import marketplace


logger = logging.getLogger('vigilant_crypto_snatch')


class HistoricalError(RuntimeError):
    pass


def retrieve_historical(then, api_key: str, coin: str, fiat: str) -> float:
    logger.debug(f'Retrieving historical price at {then} for {fiat}/{coin} …')
    timestamp = int(then.timestamp())
    url = f'https://min-api.cryptocompare.com/data/histohour?api_key={api_key}&fsym={coin.upper()}&tsym={fiat.upper()}&limit=1&toTs={timestamp}'

    r = requests.get(url)
    if r.status_code != 200:
        raise HistoricalError(f'The historical API has not returned a success: {r.status_code}')

    j = r.json()
    if len(j['Data']) == 0:
        raise HistoricalError(f'There is no payload from the historical API: {str(j)}')

    return j['Data'][-1]['close']


def search_historical(session, timestamp, api_key: str, coin: str, fiat: str) -> float:
    try:
        q = session.query(datamodel.Price).filter(
            datamodel.Price.timestamp < timestamp,
            datamodel.Price.coin == coin,
            datamodel.Price.fiat == fiat,
        ).order_by(datamodel.Price.timestamp.desc())[0]
        if q.timestamp > timestamp - datetime.timedelta(minutes=10):
            logger.debug(f'Found historical price for {timestamp} in database: {q.last} {fiat}/{coin}.')
            return q.last
    except sqlalchemy.orm.exc.NoResultFound:
        pass
    except IndexError:
        pass

    close = retrieve_historical(timestamp, api_key, coin, fiat)
    logger.debug(f'Received historical price at {timestamp} to be {close} {fiat}/{coin}.')
    price = datamodel.Price(timestamp=timestamp, last=close, coin=coin, fiat=fiat)
    session.add(price)
    session.commit()
    return close


def search_current(session, market: marketplace.Marketplace, coin: str, fiat: str) -> float:
    timestamp = datetime.datetime.now() - datetime.timedelta(seconds=5)
    try:
        q = session.query(datamodel.Price).filter(
            datamodel.Price.timestamp > timestamp,
            datamodel.Price.coin == coin,
            datamodel.Price.fiat == fiat,
        ).order_by(datamodel.Price.timestamp.desc())[0]
        logger.debug(f'Found spot price in database: {q.last} {fiat}/{coin}.')
        return q.last
    except sqlalchemy.orm.exc.NoResultFound:
        pass
    except IndexError:
        pass

    price = market.get_spot_price(coin, fiat)
    logger.debug(f'Retrieved spot price from {market.get_name()}: {price.last} {fiat}/{coin}.')
    session.add(price)
    session.commit()
    return price.last
