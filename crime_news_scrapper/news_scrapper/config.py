"""
This module provides a :py:func:`load_config`
that can be used to load the yaml config or to read yaml in python dict object.

How To Use This Module
======================

Import the :py:func:`load_config`:
   ``from config import load_config``

"""

import os
from typing import Any
import yaml

from scrapy.utils.project import get_project_settings


def get_config_path() -> str:
    """
    This will help to access settings from the Scrapy project, like user-defined arguments
    to get the path for custom config file.
    :return str: custom config file path
    """
    settings = get_project_settings()
    if os.getenv("CUSTOM_CONFIG_PATH"):
        yaml_config_path = os.getenv("CUSTOM_CONFIG_PATH")
    else:
        yaml_config_path = settings.get("CUSTOM_CONFIG_PATH")
    print(f"YAML config path: {yaml_config_path}")
    return yaml_config_path


def load_config(config_path: str) -> Any:
    """
    Safely reads yaml files and returns the resulting Python object

    :param config_path: path of the config file to load.
    :return: resulting python object after yaml read.
    """
    with open(file=config_path, mode="r", encoding="utf-8") as conf_file:
        return yaml.safe_load(conf_file)
