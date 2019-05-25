#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2019 Martin Ueding <dev@martin-ueding.de>

import argparse
import datetime
import os
import sys
import time

import bitstamp.client
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


Base = sqlalchemy.ext.declarative.declarative_base()

# Define DB columns 

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
    print(db_url)
    engine = sqlalchemy.create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    return session


def load_config():
    config_path = os.path.expanduser('~/.config/vigilant-crypto-snatch.yml')
    if not os.path.isfile(config_path):
        print('Please create the configuration file at {}.'.format(config_path))
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config

# Look up the historical price for the drop calculation
	
def search_historical(session, timestamp):
    try:
        q = session.query(Price).filter(Price.timestamp > timestamp).order_by(Price.timestamp)[0]
        print('Found', q)
        if q.timestamp < timestamp - datetime.timedelta(minutes=5):
            return q.price
        else:
            print('Not old enough, retrieving from other API.')
    except sqlalchemy.orm.exc.NoResultFound:
        pass

    # TODO
    return 10000


def main():
    options = _parse_args()

    if options.greeting:
        print(greeting)
        print()

    config = load_config()
    session = open_db_session()
    public_client = bitstamp.client.Public()

	# actual loop that first fetches the current price and calculates the drop
	
    while True:
        ticker = public_client.ticker(base='btc', quote='eur')
        now = datetime.datetime.fromtimestamp(int(ticker['timestamp']))
        price = Price(timestamp=now, last=ticker['last'])
        print('Currently:', price)

        session.add(price)
        session.commit()

        for trigger in config['triggers']:
            then = now - datetime.timedelta(minutes=trigger['minutes'])
            then_price = search_historical(session, then)
            
            critical = then_price * (1 - trigger['drop'] / 100)
            print('We had {} and look for a drop by {} %. That is {}.'.format(then_price, trigger['drop'], critical))

            if price.last < critical:
                btc = trigger['eur'] / price.last
                print('We currently have such a drop!')

                trade_count = session.query(Trade).filter(Trade.minutes == trigger['minutes'], Trade.drop == trigger['drop'], Trade.timestamp > then).count()
                print(trade_count)

				# security mechanism to prevent multiple buy orders for the same drop. If an order is excecuted for one trigger, then it's locked for a specific time before it can be executed again
				
                if trade_count == 0:
                    print('Buying {} BTC for {} EUR!'.format(btc, trigger['eur']))

                    trade = Trade(timestamp=now, minutes=trigger['minutes'], drop=trigger['drop'], btc=btc, eur=trigger['eur'])
                    session.add(trade)
                    session.commit()
                else:
                    print('This trigger was already executed.')

        time.sleep(60)


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
