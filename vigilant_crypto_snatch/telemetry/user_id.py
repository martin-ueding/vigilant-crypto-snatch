import json
import pathlib
import uuid

from .. import logger
from .. import paths


def get_user_id() -> str:
    user_id_file = pathlib.Path(paths.dirs.user_data_dir) / "user_id.json"
    logger.debug(f"User ID file: {user_id_file}")
    if user_id_file.exists():
        with open(user_id_file) as f:
            user_id = json.load(f)
        logger.debug(f"Loaded user ID: {user_id}")
    else:
        user_id = uuid.uuid4().hex
        with open(user_id_file, "w") as f:
            json.dump(user_id, f)
        logger.debug(f"Created new user ID: {user_id}")
    return user_id
