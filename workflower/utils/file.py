import logging
import os

import yaml

logger = logging.getLogger("workflower.utils.file")


def get_file_modification_date(file_path):
    return os.path.getmtime(file_path)


def get_file_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


def yaml_file_to_dict(file_path):
    try:
        with open(file_path) as yf:
            configuration_dict = yaml.safe_load(yf)
    except FileNotFoundError:
        logger.error(f"{file_path} not exist")
    return configuration_dict
