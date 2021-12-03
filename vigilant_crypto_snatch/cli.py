import click
import coloredlogs

from . import __version__


@click.group()
@click.version_option(__version__)
@click.option(
    "--loglevel",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    default="info",
    show_default=True,
    help="Controls the verbosity of logging.",
)
def main(loglevel) -> None:
    """
    Vigiliant Crypto Snatch is a
    little program that observes the current market price for your choice of currency
    pairs, looks for drastic reductions (dips) and then places buy orders.

    See https://martin-ueding.github.io/vigilant-crypto-snatch/ for the full documentation.
    """
    coloredlogs.install(level=loglevel.upper())


@main.command()
@click.option(
    "--marketplace",
    type=click.Choice(["bitstamp", "kraken"]),
    default="kraken",
    show_default=True,
    help="Marketplace to place orders on.",
)
def watch(marketplace):
    """
    Watch the market and execute defined triggers.
    """
    from .commands import watch

    watch.main(marketplace)


@main.command()
def evaluate() -> None:
    from . import streamlit_ui

    streamlit_ui.main()


@main.command()
@click.option(
    "--marketplace",
    type=click.Choice(["bitstamp", "kraken"]),
    default="kraken",
    show_default=True,
    help="Marketplace to place orders on.",
)
def test_drive(marketplace: str) -> None:
    from .commands import testdrive

    testdrive.main(marketplace)
