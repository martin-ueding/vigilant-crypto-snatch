#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import datetime

import coloredlogs

from . import factory
from . import datamodel
from . import drop
from . import telegram
from . import historical
from . import triggers


logger = logging.getLogger("vigilant_crypto_snatch")


def main():
    options = _parse_args()
    config = factory.load_config()

    if "telegram" in config:
        telegram_handler = telegram.TelegramBot(
            config["telegram"]["token"], config["telegram"]["level"]
        )
        logger.addHandler(telegram_handler)

    coloredlogs.install(level=options.loglevel.upper())

    logger.info("Starting up …")

    session = datamodel.open_user_db_session()
    market = factory.make_marketplace(options.marketplace, config)

    database_source = historical.DatabaseHistoricalSource(
        session, datetime.timedelta(minutes=5)
    )
    crypto_compare_source = historical.CryptoCompareHistoricalSource(
        config["cryptocompare"]["api_key"]
    )
    market_source = historical.MarketSource(market)
    caching_source = historical.CachingHistoricalSource(
        database_source, [market_source, crypto_compare_source], session
    )
    active_triggers = triggers.make_triggers(config, session, caching_source, market)

    trigger_loop = drop.TriggerLoop(active_triggers, config["sleep"], options.keepalive)
    trigger_loop.loop()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="https://martin-ueding.github.io/vigilant-crypto-snatch/configuration/"
    )
    parser.add_argument(
        "--marketplace", choices=["bitstamp", "kraken", "kraken-api"], default="kraken"
    )
    parser.add_argument("--keepalive", action="store_true")
    parser.add_argument(
        "--loglevel",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
    )
    options = parser.parse_args()

    return options


if __name__ == "__main__":
    main()
