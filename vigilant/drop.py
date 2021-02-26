import datetime

import vigilant.datamodel
import vigilant.historical
import vigilant.marketplace
import vigilant.logging
import vigilant.telegram


def check_for_drops(config, session, marketplace):
    """
    Actual loop that first fetches the current price and calculates the drop.
    """
    try:
        price = marketplace.get_spot_price('btc', 'eur')
    except vigilant.marketplace.TickerError as e:
        vigilant.logging.write_log(str(e))
        return

    print('Currently:', price)
    session.add(price)
    session.commit()

    for trigger in config['triggers']:
        then = price.timestamp - datetime.timedelta(minutes=trigger['minutes'])
        try:
            then_price = vigilant.historical.search_historical(session, then, config['cryptocompare']['api_key'])
        except vigilant.historical.HistoricalError:
            continue

        assert trigger['drop'] > 0, "Drop triggers must have positive percentages!"
        critical = then_price * (1 - trigger['drop'] / 100)
        print(f"We had {then_price} and look for a drop by {trigger['drop']} %. That is {critical} for the {trigger['minutes']} minutes trigger.")

        if price.last < critical:
            try_buy(marketplace, price.last, trigger, session, price.timestamp, then)


def try_buy(marketplace: vigilant.marketplace.Marketplace, price, trigger, session, now, then):
    btc = round(trigger['eur'] / price, 8)
    print('We currently have such a drop!')

    # Security mechanism to prevent multiple buy orders for the same drop. If
    # an order is executed for one trigger, then it's locked for a specific
    # time before it can be executed again.
    trade_count = session.query(vigilant.datamodel.Trade).filter(
        vigilant.datamodel.Trade.minutes == trigger['minutes'],
        vigilant.datamodel.Trade.drop == trigger['drop'],
        vigilant.datamodel.Trade.timestamp > then).count()
    if trade_count > 0:
        print('This trigger was already executed.')
        return

    print(f"Buying {btc} BTC for {trigger['eur']} EUR!")
    # Return the print notice to screen and to telegram
    buy_message = f"Buying {btc} BTC for {trigger['eur']} EUR via the {trigger['minutes']} minutes trigger because of a drop of {trigger['drop']} %"
    vigilant.telegram.telegram_bot_sendtext(buy_message)

    try:
        marketplace.place_order('btc', 'eur', btc)
    except vigilant.marketplace.BuyError as e:
        vigilant.logging.write_log(['There was an error from the Marketplace API:', str(e)])
    else:
        trade = vigilant.datamodel.Trade(
            timestamp=now,
            minutes=trigger['minutes'],
            drop=trigger['drop'],
            btc=btc,
            eur=trigger['eur'])
        session.add(trade)
        session.commit()