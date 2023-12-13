import logging
import os
from typing import Union, Any
from pyhocon import ConfigFactory, ConfigTree
from app.utils.logging import set_logging


set_logging()
logger = logging.getLogger(__name__)


class Configuration:
    data: Union[ConfigTree, Any]
    CONFIG_ENV_VAR = "CONFIG_PATH"

    def __init__(self, config_filename=None):
        self.config_filename = config_filename or os.getenv(self.CONFIG_ENV_VAR)
        self.data = ConfigFactory.parse_file(self.config_filename)

    def __getitem__(self, item):
        value = self.data[item]
        if value is None:
            raise KeyError(f"Key {item} not found in configuration file {self.config_filename}")
        return value
