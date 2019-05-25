#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2019 Martin Ueding <dev@martin-ueding.de>

import argparse
import os
import time
import sys

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


class Price(Base):
    __tablename__ = 'prices'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.Integer)
    last = sqlalchemy.Column(sqlalchemy.Float)


class Trade(Base):
    __tablename__ = 'trades'


    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.Integer)
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


def main():
    options = _parse_args()

    if options.greeting:
        print(greeting)
        print()

    config = load_config()
    session = open_db_session()
    public_client = bitstamp.client.Public()

    while True:
        ticker = public_client.ticker()

        price = Price(timestamp=int(ticker['timestamp']), last=ticker['last'])
        print(price)
        session.add(price)
        session.commit()

        time.sleep(5)


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
