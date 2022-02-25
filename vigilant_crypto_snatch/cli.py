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
def watch():
    """
    Watch the market and execute defined triggers.
    """
    from .commands import watch

    watch.main()


@main.command()
def evaluate() -> None:
    from . import streamlit_ui

    streamlit_ui.main()


@main.command()
def test_drive() -> None:
    from .commands import testdrive

    testdrive.main()


@main.command()
def report() -> None:
    from .reporting import trades

    trades.main()
