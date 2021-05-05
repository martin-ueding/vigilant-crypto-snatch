import os
import sys
import shutil

import appdirs
import yaml

from . import logger

dirs = appdirs.AppDirs(
    appname="vigilant-crypto-snatch", appauthor="Martin Ueding", roaming=True
)
config_path = os.path.join(dirs.user_config_dir, "config.yml")
old_config_path = os.path.expanduser("~/.config/vigilant-crypto-snatch.yml")
kraken_key_file = os.path.expanduser("~/.config/clikraken/kraken.key")


def load_config() -> dict:
    migrate_new_location()

    if not os.path.isfile(config_path):
        logger.error(f"Please create the configuration file at {config_path}.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    config = migrate_kraken_key(config)

    return config


def update_config(config: dict) -> None:
    with open(config_path, "w") as f:
        yaml.dump(config, f)


def migrate_new_location():
    if os.path.isfile(old_config_path) and not os.path.isfile(config_path):
        logger.info(f"Moving configuration from {old_config_path} to {config_path}.")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        shutil.move(old_config_path, config_path)


def migrate_kraken_key(config: dict) -> dict:
    if "kraken" not in config and os.path.isfile(kraken_key_file):
        logger.info("Copying your Kraken API key from clikraken to this config file.")
        with open(kraken_key_file) as f:
            key, secret = f.read().strip().split("\n")
        config["kraken"] = {"key": key, "secret": secret}
        update_config(config)
    return config
