import os

from workflower.adapters.sqlalchemy.orm import run_mappers
from workflower.config import Config

run_mappers()

if not os.path.isdir(Config.ENVIRONMENTS_DIR):
    os.makedirs(Config.ENVIRONMENTS_DIR)

if not os.path.isdir(Config.DATA_DIR):
    os.makedirs(Config.DATA_DIR)
