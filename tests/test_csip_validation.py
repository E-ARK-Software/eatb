#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from eatb import ROOT
from eatb.csip_validation import CSIPValidation

class TestCSIPValidation(unittest.TestCase):

    def test_csip_validation(self):
        ip_path = os.path.join(ROOT, 'tests/test_resources/metadata/mets/')
        rules_path = os.path.join(ROOT, "tests/test_resources/rules.xml")
        csip_validation = CSIPValidation(rules_path)
        validation_report = csip_validation.validate(ip_path)
        self.assertTrue(len(validation_report) > 0, str(len(validation_report)))
        self.assertTrue(_has_part_key('RootElement', validation_report), str(validation_report))
        self.assertTrue(len(_get_part('RootElement', validation_report)) > 0)
        self.assertTrue(_get_part('RootElement', validation_report)[0]['rule'] == "csip1")
        self.assertTrue(_get_part('RootElement', validation_report)[0]['result'])

    def test_csip_validation_with_default_rules(self):
        ip_path = os.path.join(ROOT, 'tests/test_resources/metadata/mets/')
        csip_validation = CSIPValidation()
        validation_report = csip_validation.validate(ip_path)
        self.assertTrue(len(validation_report) > 0 )
        self.assertTrue(len(validation_report) > 0)
        self.assertTrue(str(csip_validation.get_rules_file_path()).endswith("eatb/eatb/resources/validation_rules.xml"))

    def test_get_log_lines(self):
        ip_path = os.path.join(ROOT, 'tests/test_resources/metadata/mets/')
        csip_validation = CSIPValidation()
        csip_validation.validate(ip_path)
        self.assertTrue(len(csip_validation.get_log_lines()) > 0)

def _has_part_key(part_key, report):
    for report_part in report:
        if part_key in report_part:
            return True
    return False

def _get_part(part_key, report):
    for report_part in report:
        if part_key in report_part:
            return report_part[part_key]
    return None

if __name__ == '__main__':
    unittest.main()
