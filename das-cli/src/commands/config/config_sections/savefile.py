import os

from common.command import Command
from common.prompt_types import AbsolutePath
from settings.config import CONFIGFILE_PATH


def savefile_path_section() -> tuple[str, bool]:

    save_path = Command.prompt(
        "Enter the path where you will save your configuration file",
        default=CONFIGFILE_PATH,
        type=AbsolutePath(file_okay=True, dir_okay=False),
    )

    reset_file = False

    if os.path.exists(save_path):
        reset_file = Command.confirm(
            "This file already exists, would you like to reset/overwrite it's existing values?"
        )

    return (save_path, reset_file)
