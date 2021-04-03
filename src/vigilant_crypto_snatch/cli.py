import argparse
import logging
import sys

import coloredlogs

logger = logging.getLogger("vigilant_crypto_snatch")


def main():
    parser = argparse.ArgumentParser(
        description="""Vigiliant Crypto Snatch is a 
    little program that observes the current market price for your choice of currency 
    pairs, looks for drastic reductions (dips) and then places buy orders.""",
        epilog="See https://martin-ueding.github.io/vigilant-crypto-snatch/ for the full documentation.",
    )
    parser.add_argument(
        "--loglevel",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Controls the verbosity of logging. Default: %(default)s.",
    )
    parser.set_defaults(func=None)

    subcommands = parser.add_subparsers(title="subcommands")

    evaluate = subcommands.add_parser(
        "evaluate", help="Create a performance projection."
    )
    evaluate.set_defaults(func=main_evaluate)
    evaluate.add_argument(
        "--fiat",
        default="EUR",
        help="Fiat currency like EUR, USD. Case inseneitive. Default: %(default)s.",
    )
    evaluate.add_argument(
        "--coin",
        default="BTC",
        help="Cryptocurrency like BTC, ETC. Case insensitive. Default: %(default)s.",
    )

    watch = subcommands.add_parser(
        "watch", help="Watch the market and execute defined triggers."
    )
    watch.set_defaults(func=main_watch)
    watch.add_argument(
        "--marketplace",
        default="kraken",
        choices=["bitstamp", "kraken", "kraken-api"],
        help="Marketplace to place orders on. Default: %(default)s.",
    )
    watch.add_argument(
        "--keepalive",
        action="store_true",
        default=False,
        help="Ignore all Exceptions and just report them.",
    )

    options = parser.parse_args()
    if options.func is None:
        parser.print_help()
        sys.exit(1)

    coloredlogs.install(level=options.loglevel.upper())

    options.func(options)


def main_watch(options):
    from . import watchloop

    watchloop.main(options)


def main_evaluate(options) -> None:
    from . import evaluation

    evaluation.main(options)
