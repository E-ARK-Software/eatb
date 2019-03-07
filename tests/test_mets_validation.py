#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import unittest
from earchivingtoolbox.metadata.mets.MetsValidation import MetsValidation
from earchivingtoolbox import root_dir


class TestMetsValidation(unittest.TestCase):

    def test_IP_mets(self):
        mets_root_dir = os.path.join(root_dir, 'tests/test_resources/metadata/mets/')
        mets_file = 'METS.xml'
        mets_schema_file = os.path.join(root_dir, 'tests/test_resources/schemas/mets_1_11.xsd')
        premis_schema_file = os.path.join(root_dir, 'tests/test_resources/schemas/premis-v2-2.xsd')
        mets_validator = MetsValidation(mets_root_dir, mets_schema_file, premis_schema_file)
        mets_validator.validate_mets(os.path.join(mets_root_dir, mets_file))


if __name__ == '__main__':
    unittest.main()
