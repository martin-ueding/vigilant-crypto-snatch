import os
import shutil

from . import logger
from . import configuration


old_config_path = os.path.expanduser("~/.config/vigilant-crypto-snatch.yml")
kraken_key_file = os.path.expanduser("~/.config/clikraken/kraken.key")


def run_migrations() -> None:
    logger.debug('Running migrations …')
    migrate_new_location()
    migrate_kraken_key()


def migrate_new_location() -> None:
    if os.path.isfile(old_config_path) and not os.path.isfile(
        configuration.config_path
    ):
        logger.info(
            f"Moving configuration from {old_config_path} to {configuration.config_path}."
        )
        os.makedirs(os.path.dirname(configuration.config_path), exist_ok=True)
        shutil.move(old_config_path, configuration.config_path)


def migrate_kraken_key() -> None:
    config = configuration.load_config()
    if "kraken" not in config and os.path.isfile(kraken_key_file):
        logger.info("Copying your Kraken API key from clikraken to this config file.")
        with open(kraken_key_file) as f:
            key, secret = f.read().strip().split("\n")
        config["kraken"] = {"key": key, "secret": secret}
        configuration.update_config(config)
