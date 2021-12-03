import os
import pathlib

import appdirs


dirs = appdirs.AppDirs(
    appname="vigilant-crypto-snatch", appauthor="Martin Ueding", roaming=True
)
config_path = os.path.join(dirs.user_config_dir, "config.yml")
user_db_path = os.path.join(dirs.user_data_dir, "db.sqlite")
chat_id_path = pathlib.Path(dirs.user_data_dir) / "telegram_chat_id.json"


def report_app_dirs() -> None:  # pragma: no cover
    print(f"user_config_dir: {dirs.user_config_dir}")
    print(f"user_log_dir: {dirs.user_log_dir}")
    print(f"user_data_dir: {dirs.user_data_dir}")
    print(f"user_cache_dir: {dirs.user_cache_dir}")
    print(f"user_state_dir: {dirs.user_state_dir}")
