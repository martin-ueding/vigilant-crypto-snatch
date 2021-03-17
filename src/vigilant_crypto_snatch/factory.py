import logging
import os
import sys

import sqlalchemy.orm
import yaml

from . import (
    cli,
    datamodel,
    marketplace,
    bitstamp_adaptor,
    clikraken_adaptor_api,
    clikraken_adaptor_cli,
)


logger = logging.getLogger("vigilant_crypto_snatch")
db_path = os.path.expanduser("~/.local/share/vigilant-crypto-snatch/db.sqlite")
config_path = os.path.expanduser("~/.config/vigilant-crypto-snatch.yml")


def make_marketplace(marketplace_str: str, config: dict) -> marketplace.Marketplace:
    if marketplace_str == "bitstamp":
        return bitstamp_adaptor.BitstampMarketplace(
            config["bitstamp"]["username"],
            config["bitstamp"]["key"],
            config["bitstamp"]["secret"],
        )
    elif marketplace_str == "kraken-api":
        return clikraken_adaptor_api.KrakenMarketplace()
    elif marketplace_str == "kraken":
        return clikraken_adaptor_cli.KrakenMarketplace()
    else:
        raise RuntimeError(f"Unknown market place {marketplace_str}!")


def load_config() -> dict:
    if not os.path.isfile(config_path):
        logger.error(f"Please create the configuration file at {config_path}.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


def open_db_session() -> sqlalchemy.orm.Session:
    if not os.path.isdir(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    assert os.path.isdir(os.path.dirname(db_path))

    db_url = "sqlite:///{}".format(db_path)
    engine = sqlalchemy.create_engine(db_url)
    datamodel.Base.metadata.create_all(engine)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    return session
