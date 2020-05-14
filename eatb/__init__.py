""" Root E-ARK Toolbox module. """
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from logging.config import fileConfig

ROOT = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

fileConfig(os.path.join(ROOT, 'logging_config.ini'))
LOGGER = logging.getLogger()
