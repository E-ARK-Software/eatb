#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import configparser
from eatb import root_dir


config = configparser.ConfigParser()
config['DEFAULT'] = {}
config.sections()

config.read(os.path.join(root_dir, 'settings/settings.cfg'))

application_name = config.get('global', 'application_name')
application_version = config.get('global', 'application_version')

fido_enabled = bool(eval(config.get('format', 'fido_enabled')))
