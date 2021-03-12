#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time

import yaml

import vigilant.bitstamp_adaptor
import vigilant.datamodel
import vigilant.drop
import vigilant.greeting
import vigilant.kraken_adaptor
import vigilant.logging
import vigilant.marketplace


def load_config():
    config_path = os.path.expanduser('~/.config/vigilant-crypto-snatch.yml')
    if not os.path.isfile(config_path):
        print(f"Please create the configuration file at {config_path}.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


def main():
    options = _parse_args()

    vigilant.logging.write_log(['Starting up.'])

    if options.greeting:
        print(vigilant.greeting.greeting)
        print()

    config = load_config()
    session = vigilant.datamodel.open_db_session()

    if options.marketplace == 'bitstamp':
        marketplace = vigilant.bitstamp_adaptor.BitstampMarketplace(
            config['bitstamp']['username'], config['bitstamp']['key'], config['bitstamp']['secret'])
    elif options.marketplace == 'kraken':
        marketplace = vigilant.kraken_adaptor.KrakenMarketplace()
    else:
        raise RuntimeError(f'Unknown market place {options.marketplace}!')

    while True:
        vigilant.drop.check_for_drops(config, session, marketplace)
        time.sleep(config['sleep'])


def _parse_args():
    """
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--greeting', action='store_true',
                        help='Show an unnecessary long greeting message during startup.')
    parser.add_argument('--marketplace', choices=['bitstamp', 'kraken'], default='kraken')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
