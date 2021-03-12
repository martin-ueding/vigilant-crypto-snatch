import datetime

from . import datamodel
from . import historical
from . import marketplace
from . import logging
from . import telegram


def check_for_drops(config, session, market: marketplace.Marketplace):
    """
    Actual loop that first fetches the current price and calculates the drop.
    """
    currency_pairs = config.get('currency_pairs', [('BTC', 'EUR')])
    for coin, fiat in currency_pairs:
        coin = coin.upper()
        fiat = fiat.upper()
        try:
            price = market.get_spot_price(coin, fiat)
        except marketplace.TickerError as e:
            logging.write_log([str(e)])
            return

        print('Currently:', price)
        session.add(price)
        session.commit()

        for trigger in config['triggers']:
            then = price.timestamp - datetime.timedelta(minutes=trigger['minutes'])
            try:
                then_price = historical.search_historical(session, then, config['cryptocompare']['api_key'], coin, fiat)
            except historical.HistoricalError:
                continue

            assert trigger['drop'] > 0, "Drop triggers must have positive percentages!"
            critical = then_price * (1 - trigger['drop'] / 100)
            print(f"We had {then_price} and look for a drop by {trigger['drop']} %. That is {critical} for the {trigger['minutes']} minutes trigger.")

            if price.last < critical:
                try_buy(config, market, price.last, trigger, session, price.timestamp, then, coin, fiat)


def try_buy(config: dict, market: marketplace.Marketplace, price: float, trigger: dict, session, now, then, coin: str, fiat: str):
    volume_fiat = trigger['volume_fiat'] if 'volume_fiat' in trigger else trigger['eur']
    volume_coin = round(volume_fiat / price, 8)
    print('We currently have such a drop!')

    # Security mechanism to prevent multiple buy orders for the same drop. If
    # an order is executed for one trigger, then it's locked for a specific
    # time before it can be executed again.
    trade_count = session.query(datamodel.Trade).filter(
        datamodel.Trade.minutes == trigger['minutes'],
        datamodel.Trade.drop == trigger['drop'],
        datamodel.Trade.timestamp > then,
        datamodel.Trade.coin == coin,
        datamodel.Trade.fiat == fiat).count()
    if trade_count > 0:
        print('This trigger was already executed.')
        return

    print(f"Buying {volume_coin} {coin} for {volume_fiat} {fiat}!")
    # Return the print notice to screen and to telegram
    buy_message = f"Buying {volume_coin} {coin} for {volume_fiat} {fiat} on {market.get_name()} via the {trigger['minutes']} minutes trigger because of a drop of {trigger['drop']} %."
    telegram.telegram_bot_sendtext(config, buy_message)

    try:
        market.place_order(coin, fiat, volume_coin)
    except marketplace.BuyError as e:
        logging.write_log(['There was an error from the Marketplace API:', str(e)])
    else:
        trade = datamodel.Trade(
            timestamp=now,
            minutes=trigger['minutes'],
            drop=trigger['drop'],
            volume_coin=volume_coin,
            volume_fiat=volume_fiat,
            coin=coin,
            fiat=fiat)
        session.add(trade)
        session.commit()
