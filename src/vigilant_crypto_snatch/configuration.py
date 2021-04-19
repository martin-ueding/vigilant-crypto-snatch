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


def load_config() -> dict:
    if os.path.isfile(old_config_path) and not os.path.isfile(config_path):
        logger.info(f"Moving configuration from {old_config_path} to {config_path}.")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        shutil.move(old_config_path, config_path)

    if not os.path.isfile(config_path):
        logger.error(f"Please create the configuration file at {config_path}.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config


def update_config(config: dict) -> None:
    with open(config_path, "w") as f:
        yaml.dump(config, f)
