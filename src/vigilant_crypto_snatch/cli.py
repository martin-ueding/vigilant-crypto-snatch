#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import datetime

import coloredlogs
import click

from . import factory
from . import datamodel
from . import watch
from . import telegram
from . import historical
from . import triggers
from . import __version__


logger = logging.getLogger("vigilant_crypto_snatch")


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--loglevel",
    default="info",
    help="Controls the verbosity of logging.",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
)
def cli(loglevel):
    config = factory.load_config()

    if "telegram" in config:
        telegram_handler = telegram.TelegramBot(
            config["telegram"]["token"], config["telegram"]["level"]
        )
        logger.addHandler(telegram_handler)

    coloredlogs.install(level=loglevel.upper())


@cli.command()
@click.option(
    "--marketplace",
    default="kraken",
    help="Marketplace to place orders on.",
    type=click.Choice(["bitstamp", "kraken", "kraken-api"], case_sensitive=True),
)
@click.option(
    "--keepalive/--no-keepalive",
    default=False,
    help="Ignore all Exceptions and just report them.",
)
def watch(marketplace, keepalive):
    """
    Watches the market and automatically places buy orders.
    """
    logger.info("Starting up …")

    session = datamodel.open_user_db_session()
    config = factory.load_config()
    market = factory.make_marketplace(marketplace, config)

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

    trigger_loop = watch.TriggerLoop(active_triggers, config["sleep"], keepalive)
    trigger_loop.loop()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="https://martin-ueding.github.io/vigilant-crypto-snatch/configuration/"
    )
    parser.add_argument(
        "--marketplace",
    )
    parser.add_argument("--keepalive", action="store_true")
    options = parser.parse_args()

    return options
