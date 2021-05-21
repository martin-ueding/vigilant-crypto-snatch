import os
import shutil

from . import logger
from . import configuration


old_config_path = os.path.expanduser("~/.config/vigilant-crypto-snatch.yml")
kraken_key_file = os.path.expanduser("~/.config/clikraken/kraken.key")
old_user_db_path = os.path.expanduser("~/.local/share/vigilant-crypto-snatch/db.sqlite")


def run_migrations() -> None:
    logger.debug("Running migrations …")
    migrate_new_location()
    migrate_kraken_key()
    move_database()


def needs_moving(old_path: str, new_path: str) -> bool:
    return os.path.isfile(old_path) and not os.path.isfile(new_path)


def move_file_if_needed(old_path: str, new_path: str) -> None:
    if needs_moving(old_path, new_path):
        logger.info(f"Moving file from {old_path} to {new_path}.")
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)


def migrate_new_location() -> None:
    move_file_if_needed(old_config_path, configuration.config_path)


def move_database() -> None:
    needs_moving(old_user_db_path, configuration.user_db_path)


def migrate_kraken_key() -> None:
    config = configuration.load_config()
    if "kraken" not in config and os.path.isfile(kraken_key_file):
        logger.info("Copying your Kraken API key from clikraken to this config file.")
        with open(kraken_key_file) as f:
            key, secret = f.read().strip().split("\n")
        config["kraken"] = {"key": key, "secret": secret}
        configuration.update_config(config)
