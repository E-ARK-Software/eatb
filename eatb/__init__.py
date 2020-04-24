""" Root E-ARK Toolbox module. """
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

ROOT = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
LOGGER = logging.getLogger(__name__)
