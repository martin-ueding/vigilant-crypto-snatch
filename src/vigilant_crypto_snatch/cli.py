import click
import coloredlogs


@click.group()
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
@click.option(
    "--keepalive/--no-keepalive",
    default=False,
    show_default=True,
    help="Ignore all Exceptions and just report them.",
)
@click.option(
    "--one-shot/--no-one-shot",
    default=False,
    show_default=True,
    help="Only check once and then exit.",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    show_default=True,
    help="Do not place actual orders to the marketplace.",
)
def watch(marketplace, keepalive, one_shot, dry_run):
    """
    Watch the market and execute defined triggers.
    """
    from .commands import watch

    watch.main(marketplace, keepalive, one_shot, dry_run)


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
    from vigilant_crypto_snatch.commands import testdrive

    testdrive.main(marketplace)
