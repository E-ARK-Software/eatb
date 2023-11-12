#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from eatb import ROOT
from eatb.metadata.parsed_mets import ParsedMets

test_dir = os.path.join(ROOT, 'tests/test_resources/metadata/mets/')
test_file = test_dir + 'METS_filesec.xml'


class TestParsedMets(unittest.TestCase):
    pmets = ParsedMets(test_dir)
    pmets.load_mets(test_file)
    def test_validate_files_size(self):
        """
        Must not validate if the files listed in the METS file does not match the actual file size
        """
        actual = self.pmets.mets_tree.getroot().tag
        self.assertEqual(actual, "{http://www.loc.gov/METS/}mets", "Root tag 'mets' not found")

    def test_get_file_elements(self):
        """
        File elements list must have one file element
        """
        file_elements = self.pmets.get_file_elements()
        self.assertIsNotNone(file_elements, "File elements must not be None")
        self.assertEqual(len(file_elements), 1, "File elements list must have one file element")

    def test_get_first_file_element(self):
        """
        Must return first file element
        """
        file_element = self.pmets.get_first_file_element()
        self.assertEqual(file_element.tag, "{http://www.loc.gov/METS/}file", "Must return a file element")

    def test_get_package_type(self):
        """
        Must return first file element
        """
        self.assertEqual("SIP", self.pmets.get_package_type())


if __name__ == '__main__':
    unittest.main()
