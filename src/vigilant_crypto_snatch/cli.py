#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import datetime

import coloredlogs
import click

from . import factory
from . import datamodel
from . import watchloop
from . import telegram
from . import historical
from . import configuration
from . import triggers
from . import configuration
from . import __version__

logger = logging.getLogger("vigilant_crypto_snatch")


def add_telegram_logger() -> None:
    config = configuration.load_config()
    if "telegram" in config:
        telegram_handler = telegram.TelegramBot(
            config["telegram"]["token"],
            config["telegram"]["level"],
            config["telegram"].get("chat_id", None),
        )
        logger.addHandler(telegram_handler)

        if not "chat_id" in config["telegram"]:
            config["telegram"]["chat_id"] = telegram_handler.chat_id
            configuration.update_config(config)


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
    add_telegram_logger()
    logger.info("Starting up …")

    session = datamodel.open_user_db_session()
    config = configuration.load_config()
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

    trigger_loop = watchloop.TriggerLoop(active_triggers, config["sleep"], keepalive)
    trigger_loop.loop()


@cli.command()
@click.option(
    "--coin",
    default="BTC",
    help="Cryptocurrency like BTC, ETC. Case insensitive. Defaults to BTC.",
)
@click.option(
    "--fiat",
    default="EUR",
    help="Fiat currency like EUR, USD. Case inseneitive. Defaults to EUR.",
)
def evaluate(coin: str, fiat: str) -> None:
    """
    Evaluates the strategy on historic data.
    """
    config = configuration.load_config()
    from . import evaluation

    evaluation.make_report(coin, fiat, config["cryptocompare"]["api_key"])
