import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import logging
from logging.config import fileConfig

root_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

fileConfig(os.path.join(root_dir, 'logging_config.ini'))
logger = logging.getLogger(__name__)
