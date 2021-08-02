import os
import sys
import typing

import appdirs
import yaml

from . import logger

dirs = appdirs.AppDirs(
    appname="vigilant-crypto-snatch", appauthor="Martin Ueding", roaming=True
)
config_path = os.path.join(dirs.user_config_dir, "config.yml")
user_db_path = os.path.join(dirs.user_data_dir, "db.sqlite")


def report_app_dirs() -> None:
    print(f"user_config_dir: {dirs.user_config_dir}")
    print(f"user_log_dir: {dirs.user_log_dir}")
    print(f"user_data_dir: {dirs.user_data_dir}")
    print(f"user_cache_dir: {dirs.user_cache_dir}")
    print(f"user_state_dir: {dirs.user_state_dir}")


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


def get_used_currencies(config: dict) -> typing.Set[str]:
    result = set()
    for trigger_spec in config["triggers"]:
        result.add(trigger_spec["fiat"].upper())
        result.add(trigger_spec["coin"].upper())
    logger.debug(f"Currencies used in triggers: {result}")
    return result
