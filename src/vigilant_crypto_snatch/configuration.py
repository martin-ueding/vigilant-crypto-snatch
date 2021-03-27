import logging
import os
import sys

import appdirs
import yaml

logger = logging.getLogger("vigilant_crypto_snatch")

dirs = appdirs.AppDirs(appname="vigilant-crypto-snatch", appauthor="Martin Ueding", roaming=True)
config_path = os.path.join(dirs.user_config_dir, "config.yml")


def load_config() -> dict:
    if not os.path.isfile(config_path):
        logger.error(f"Please create the configuration file at {config_path}.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


def update_config(config: dict) -> None:
    with open(config_path, "w") as f:
        yaml.dump(config, f)