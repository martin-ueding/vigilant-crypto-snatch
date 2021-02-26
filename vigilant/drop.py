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
    currency_pairs = config.get('currency_pairs', [('BTC', 'EUR')])
    for coin, fiat in currency_pairs:
        coin = coin.upper()
        fiat = fiat.upper()
        try:
            price = marketplace.get_spot_price(coin, fiat)
        except vigilant.marketplace.TickerError as e:
            vigilant.logging.write_log(str(e))
            return

        print('Currently:', price)
        session.add(price)
        session.commit()

        for trigger in config['triggers']:
            then = price.timestamp - datetime.timedelta(minutes=trigger['minutes'])
            try:
                then_price = vigilant.historical.search_historical(session, then, config['cryptocompare']['api_key'], coin, fiat)
            except vigilant.historical.HistoricalError:
                continue

            assert trigger['drop'] > 0, "Drop triggers must have positive percentages!"
            critical = then_price * (1 - trigger['drop'] / 100)
            print(f"We had {then_price} and look for a drop by {trigger['drop']} %. That is {critical} for the {trigger['minutes']} minutes trigger.")

            if price.last < critical:
                try_buy(marketplace, price.last, trigger, session, price.timestamp, then, coin, fiat)


def try_buy(marketplace: vigilant.marketplace.Marketplace, price: float, trigger: dict, session, now, then, coin: str, fiat: str):
    volume_fiat = trigger['volume_fiat'] if 'volume_fiat' in trigger else trigger['eur']
    volume_coin = round(volume_fiat / price, 8)
    print('We currently have such a drop!')

    # Security mechanism to prevent multiple buy orders for the same drop. If
    # an order is executed for one trigger, then it's locked for a specific
    # time before it can be executed again.
    trade_count = session.query(vigilant.datamodel.Trade).filter(
        vigilant.datamodel.Trade.minutes == trigger['minutes'],
        vigilant.datamodel.Trade.drop == trigger['drop'],
        vigilant.datamodel.Trade.timestamp > then,
        vigilant.datamodel.Trade.coin == coin,
        vigilant.datamodel.Trade.fiat == fiat).count()
    if trade_count > 0:
        print('This trigger was already executed.')
        return

    print(f"Buying {volume_coin} {coin} for {volume_fiat} {fiat}!")
    # Return the print notice to screen and to telegram
    buy_message = f"Buying {volume_coin} {coin} for {volume_fiat} {fiat} via the {trigger['minutes']} minutes trigger because of a drop of {trigger['drop']} %"
    vigilant.telegram.telegram_bot_sendtext(buy_message)

    try:
        marketplace.place_order(coin, fiat, volume_coin)
    except vigilant.marketplace.BuyError as e:
        vigilant.logging.write_log(['There was an error from the Marketplace API:', str(e)])
    else:
        trade = vigilant.datamodel.Trade(
            timestamp=now,
            minutes=trigger['minutes'],
            drop=trigger['drop'],
            volume_coin=volume_coin,
            volume_fiat=volume_fiat,
            coin=coin,
            fiat=fiat)
        session.add(trade)
        session.commit()