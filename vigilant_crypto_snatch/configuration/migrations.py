import os
import shutil

from .. import logger


def run_migrations() -> None:
    logger.debug("Running migrations …")


def needs_moving(old_path: str, new_path: str) -> bool:
    return os.path.isfile(old_path) and not os.path.isfile(new_path)


def move_file_if_needed(old_path: str, new_path: str) -> None:
    if needs_moving(old_path, new_path):
        logger.info(f"Moving file from {old_path} to {new_path}.")
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
