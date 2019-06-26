#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2019 Martin Ueding <dev@martin-ueding.de>

import argparse
import datetime
import os
import pprint
import sys
import time

import bitstamp.client
import requests
import sqlalchemy
import sqlalchemy.ext.declarative
import yaml


greeting = r"""
Welcome to

           $$\    $$\$$\         $$\$$\                   $$\     
           $$ |   $$ \__|        \__$$ |                  $$ |    
           $$ |   $$ $$\ $$$$$$\ $$\$$ |$$$$$$\ $$$$$$$\$$$$$$\   
           \$$\  $$  $$ $$  __$$\$$ $$ |\____$$\$$  __$$\_$$  _|  
            \$$\$$  /$$ $$ /  $$ $$ $$ |$$$$$$$ $$ |  $$ |$$ |    
             \$$$  / $$ $$ |  $$ $$ $$ $$  __$$ $$ |  $$ |$$ |$$\ 
              \$  /  $$ \$$$$$$$ $$ $$ \$$$$$$$ $$ |  $$ |\$$$$  |
               \_/   \__|\____$$ \__\__|\_______\__|  \__| \____/ 
                        $$\   $$ |                                
                        \$$$$$$  |                                
                         \______/                                 
           
           
            $$$$$$\                             $$\              
           $$  __$$\                            $$ |             
           $$ /  \__|$$$$$$\ $$\   $$\ $$$$$$\$$$$$$\   $$$$$$\  
           $$ |     $$  __$$\$$ |  $$ $$  __$$\_$$  _| $$  __$$\ 
           $$ |     $$ |  \__$$ |  $$ $$ /  $$ |$$ |   $$ /  $$ |
           $$ |  $$\$$ |     $$ |  $$ $$ |  $$ |$$ |$$\$$ |  $$ |
           \$$$$$$  $$ |     \$$$$$$$ $$$$$$$  |\$$$$  \$$$$$$  |
            \______/\__|      \____$$ $$  ____/  \____/ \______/ 
                             $$\   $$ $$ |                       
                             \$$$$$$  $$ |                       
                              \______/\__|                       
           
           
            $$$$$$\                    $$\             $$\       
           $$  __$$\                   $$ |            $$ |      
           $$ /  \__$$$$$$$\  $$$$$$\$$$$$$\   $$$$$$$\$$$$$$$\  
           \$$$$$$\ $$  __$$\ \____$$\_$$  _| $$  _____$$  __$$\ 
            \____$$\$$ |  $$ |$$$$$$$ |$$ |   $$ /     $$ |  $$ |
           $$\   $$ $$ |  $$ $$  __$$ |$$ |$$\$$ |     $$ |  $$ |
           \$$$$$$  $$ |  $$ \$$$$$$$ |\$$$$  \$$$$$$$\$$ |  $$ |
            \______/\__|  \__|\_______| \____/ \_______\__|  \__|
  

MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWNMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMWOO0MMMMMMMMMMMMM;  NMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMXOxkKMNKMMMMMMMMM:  NMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMWWMMWdx,MloMMMMMMMMMKl NMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMNc,dKK0ol,K:oKXMMWWMMMMMxWMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMKkWMMMX0Wc,',''.;,;..;KN;NMMMWOOMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMKNNKkkl' . .  kO;:cl:;dd;'',...'.'....0cKMMMMMNXOl:..::KMMMMMMMMMMMMMMMMMMMM
MM0dko:;dddollccccc::::;''''''........'',;;;;;;;;;;;;;;;;:cldk0XWo..,;dcckMMMX
MWKl;,,,.;,',;,',',,,',;,,,,','.....'',,,'''''''''''''''''''''.'',clcOO:;xKkON
MWNMMMMWWWWNNNX0'OXXXXNNNNNNXXKK000OOOOOOO0000KKKKXXXXXX0kKK0d;;dOxOKXXNWo;lMK
MMMMMMMMMMMMMMMWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMXXMMMMMMMMMWWWMM
""".strip()


###############################################################################
#                                  Database                                   #
###############################################################################

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


###############################################################################
#                                External APIs                                #
###############################################################################


class HistoricalError(RuntimeError): pass


def retrieve_historical(then, api_key):
    '''
    If the DB doesn't have the requested data, it requests it from
    Cryptocompare via their API. You have to use your own API key. It's to be
    inserted into the sample_config!!
    '''
    timestamp = then.timestamp()
    url = 'https://min-api.cryptocompare.com/data/histohour?api_key={}&fsym=BTC&tsym=EUR&limit=1&toTs={}'.format(
        api_key,
        timestamp)

    r = requests.get(url)
    if r.status_code != 200:
        write_log(['The historical API has not returned a success.', 'Status was {}.'.format(r.status_code)])
        raise HistoricalError()

    j = r.json()
    if len(j['Data']) == 0:
        write_log(['There is no payload in from the historical API', str(j)])
        raise HistoricalError()

    return j['Data'][-1]['close']

	
def search_historical(session, timestamp, api_key):
    '''
    Look up the historical price for the drop calculation
    '''
    try:
        q = session.query(Price).filter(Price.timestamp > timestamp).order_by(Price.timestamp.desc())[0]
        if q.timestamp < timestamp + datetime.timedelta(minutes=10):
            return q.price
    except sqlalchemy.orm.exc.NoResultFound:
        pass

    close = retrieve_historical(timestamp, api_key)

    price = Price(timestamp=timestamp, last=close)
    session.add(price)
    session.commit()
    return close


def try_buy(trading_client, price, trigger, session, now, then):
    btc = round(trigger['eur'] / price, 8)
    print('We currently have such a drop!')

    # Security mechanism to prevent multiple buy orders for the same drop. If
    # an order is excecuted for one trigger, then it's locked for a specific
    # time before it can be executed again.
    trade_count = session.query(Trade).filter(Trade.minutes == trigger['minutes'], Trade.drop == trigger['drop'], Trade.timestamp > then).count()
    if trade_count > 0:
        print('This trigger was already executed.')
        return

    print('Buying {} BTC for {} EUR!'.format(btc, trigger['eur']))

    try:
        buy(trading_client, btc)
    except bitstamp.client.BitstampError as e:
        write_log(['There was an error from the Bitstamp API:', str(e)])
    else:
        trade = Trade(
            timestamp=now,
            minutes=trigger['minutes'],
            drop=trigger['drop'],
            btc=btc,
            eur=trigger['eur'])
        session.add(trade)
        session.commit()


def buy(trading_client, btc):
    response = trading_client.buy_market_order(btc, base='btc', quote='eur')
    pprint.pprint(response)


###############################################################################
#                                 Miscellanea                                 #
###############################################################################


def load_config():
    config_path = os.path.expanduser('~/.config/vigilant-crypto-snatch.yml')
    if not os.path.isfile(config_path):
        print('Please create the configuration file at {}.'.format(config_path))
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


def write_log(lines):
    '''
    Appends the given list of lines to the log file.

    :param lines list(str):
    '''
    path = os.path.expanduser('~/.local/share/vigilant-crypto-snatch/log.txt')
    now = datetime.datetime.now()

    with open(path, 'a') as f:
        f.write(now.isoformat() + '\n')
        for line in lines:
            f.write('  ' + line.strip() + '\n')
            print(line)


def check_for_drops(config, session, public_client, trading_client):
    '''
    Actual loop that first fetches the current price and calculates the drop.
    '''
    ticker = public_client.ticker(base='btc', quote='eur')
    now = datetime.datetime.fromtimestamp(int(ticker['timestamp']))
    try:
        price = Price(timestamp=now, last=ticker['last'])
    except requests.exceptions.ChunkedEncodingError as e:
        write_log(['Exception in Bitstamp Ticker reqest.', str(e)])
        return
    except requests.exceptions.HTTPError as e:
        write_log(['Exception in Bitstamp Ticker reqest.', str(e)])
        return
    except requests.exceptions.ChunkedEncodingError as e:
        write_log(['Exception in Bitstamp Ticker reqest.', str(e)])
        return
    except urllib3.exceptions.ProtocolError as e:
        write_log(['Exception in Bitstamp Ticker reqest.', str(e)])
        return
    except http.client.RemoteDisconnected as e:
        write_log(['Exception in Bitstamp Ticker reqest.', str(e)])
        return
    except OpenSSL.SSL.SysCallError as e:
        write_log(['Exception in Bitstamp Ticker reqest.', str(e)])
        return


    print('Currently:', price)

    session.add(price)
    session.commit()

    for trigger in config['triggers']:
        then = now - datetime.timedelta(minutes=trigger['minutes'])
        try:
            then_price = search_historical(session, then, config['cryptocompare']['api_key'])
        except HistoricalError:
            continue
        
        critical = then_price * (1 - trigger['drop'] / 100)
        print('We had {} and look for a drop by {} %. That is {} for the {} minutes trigger.'.format(then_price, trigger['drop'], critical, trigger['minutes']))

        if price.last < critical:
            try_buy(trading_client, price.last, trigger, session, now, then)


##Telegram Bot Notice

def telegram_bot_sendtext(bot_message):
    
    bot_token = 'here'   #Your Bot Token from Telegram 
    bot_chatID = 'here'     #The Chat ID 
    send_text = 'https://api.telegram.org/bot' + bot_http + '/sendMessage?chat_id=' + bot_chat + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()

def report():
##    my_price = print()       Replace this with the current price 
    my_message = 'Buying {} BTC for {} EUR on the {} because of a drop of {} %'.format(btc, trigger['eur'], trigger['minutes'], trigger['drop'])   ## Customize your message
    telegram_bot_sendtext(my_message)

##End Telegram Bot Notice - Standard Report can be placed with report() - Be sure to customize your message and price info 


def main():
    options = _parse_args()

    write_log(['Starting up.'])

    if options.greeting:
        print(greeting)
        print()

    config = load_config()
    session = open_db_session()
    public_client = bitstamp.client.Public()
    trading_client = bitstamp.client.Trading(
        username=config['bitstamp']['username'],
        key=config['bitstamp']['key'],
        secret=config['bitstamp']['secret'])

    while True:
        check_for_drops(config, session, public_client, trading_client)
        time.sleep(config['sleep'])


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--greeting', action='store_true', help='Show an unnecessary long greeting message during startup.')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
