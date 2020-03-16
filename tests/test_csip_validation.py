#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from eatb.validation.csip_validation import CSIPValidation
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import unittest
from eatb import root_dir


class TestCSIPValidation(unittest.TestCase):

    def test_csip_validation(self):
        ip_path = os.path.join(root_dir, 'tests/test_resources/metadata/mets/')
        rules_path = os.path.join(root_dir, "tests/rules.xml")
        csip_validation = CSIPValidation(rules_path)
        validation_report = csip_validation.validate(ip_path)
        self.assertTrue(len(validation_report) > 0 )
        self.assertTrue('RootElement' in validation_report[0])
        self.assertTrue(len(validation_report[0]['RootElement']) > 0)
        self.assertTrue(validation_report[0]['RootElement'][0]['rule'] == "csip1")
        self.assertTrue(validation_report[0]['RootElement'][0]['result'])

    def test_csip_validation_with_default_rules(self):
        ip_path = os.path.join(root_dir, 'tests/test_resources/metadata/mets/')
        csip_validation = CSIPValidation()
        validation_report = csip_validation.validate(ip_path)
        self.assertTrue(len(validation_report) > 0 )
        self.assertTrue(len(validation_report) > 0)
        self.assertTrue(csip_validation.get_rules_file_path().endswith("eatb/eatb/resources/validation_rules.xml"))

    def test_get_log_lines(self):
        ip_path = os.path.join(root_dir, 'tests/test_resources/metadata/mets/')
        csip_validation = CSIPValidation()
        csip_validation.validate(ip_path)
        self.assertTrue(len(csip_validation.get_log_lines()) > 0)




if __name__ == '__main__':
    unittest.main()
