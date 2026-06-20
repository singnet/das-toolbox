import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path
from fastapi import UploadFile

from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import CONFIG_DIR, DEFAULT_WEBCONFIG_PATH
from shared.exceptions.custom_exceptions import DasCliCommandException
from shared.dtos.configuration_entries_dto import ConfigurationEntriesDto
from shared.mappers.das_config_mapper import ConfigMapper

class ConfigServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    async def save_config(self, configuration_entries : ConfigurationEntriesDto):
        result = ConfigMapper.build_config(configuration_entries)

        print(result)

        return result

    async def load_config(self):
        try:
            with open(DEFAULT_WEBCONFIG_PATH, "r") as f:
                config_dict = json.load(f)

            if isinstance(config_dict, list):
                config_dict = config_dict[0]

            return config_dict
        except Exception:
            raise Exception("Error while trying to load config file.")

