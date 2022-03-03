import logging
import os

import yaml

logger = logging.getLogger("workflower.utils.file")


def get_file_name(file_path: str) -> int:
    """
    Get file name from path without it's extension.
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def get_file_modification_date(file_path: str) -> int:
    """
    Get file modification seconds since epoch from path without it's extension.
    """
    return os.path.getmtime(file_path)


def yaml_file_to_dict(file_path: str) -> dict:
    """
    Return a dict from yaml file's path.
    """
    try:
        with open(file_path) as yf:
            configuration_dict = yaml.safe_load(yf)
        return configuration_dict
    except FileNotFoundError:
        logger.error(f"{file_path} not exist")
