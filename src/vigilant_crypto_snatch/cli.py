#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time

import yaml

from . import marketplace_factory
from . import datamodel
from . import drop
from . import greeting
from . import logging


def load_config() -> dict:
    config_path = os.path.expanduser('~/.config/vigilant-crypto-snatch.yml')
    if not os.path.isfile(config_path):
        print(f"Please create the configuration file at {config_path}.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


def main():
    options = _parse_args()

    logging.write_log(['Starting up.'])

    if options.greeting:
        print(greeting.greeting)
        print()

    config = load_config()
    session = datamodel.open_db_session()

    market = marketplace_factory.make_marketplace(options.marketplace, config)
    while True:
        drop.check_for_drops(config, session, market)
        time.sleep(config['sleep'])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--greeting', action='store_true',
                        help='Show an unnecessary long greeting message during startup.')
    parser.add_argument('--marketplace', choices=['bitstamp', 'kraken', 'kraken-cli'], default='kraken')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
