#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import os

from eatb import ROOT

config = configparser.ConfigParser()
config['DEFAULT'] = {}
config.sections()

config.read(os.path.join(ROOT, 'eatb/settings.cfg'))

application_name = config.get('global', 'application_name')
application_version = config.get('global', 'application_version')

fido_enabled = bool(eval(config.get('format', 'fido_enabled')))

format_files_cfg = config.get('format', 'format_files')

validation_profile = config.get('validation', 'validation_profile')

