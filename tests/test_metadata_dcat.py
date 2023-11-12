#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from eatb import ROOT
from eatb.metadata.parsed_dcat import ParsedDcat
from eatb.utils.fileutils import read_file_content


class TestParsedDcat(unittest.TestCase):
    test_dir = os.path.join(ROOT, 'tests/test_resources/')

    def test_get_dataset_property_value(self):
        """
        Test get dataset property value
        """
        xml_content = read_file_content(os.path.join(TestParsedDcat.test_dir, 'metadata/dcat/dcat.xml'))
        pead = ParsedDcat(xml_content.encode('utf-8'))
        title = pead.get_dataset_property_value("dct:title")
        print(title)

    def test_get_dataset_property_values(self):
        """
        Test get dataset property values
        """
        xml_content = read_file_content(
            os.path.join(TestParsedDcat.test_dir, TestParsedDcat.test_dir + 'metadata/dcat/dcat.xml'))
        pead = ParsedDcat(xml_content.encode('utf-8'))
        titles = pead.get_dataset_property_values(
            ["dct:title", "dct:description", "dcat:keyword", "dcat:theme", "dmav:User_Generated_Tags/dcat:keyword",
             "dct:publisher/foaf:Organization/foaf:name", "dcat:contactPoint/vcard:Organization/vcard:fn"]
        )
        print(titles)

    def test_get_distribution_property_values(self):
        """
        Test get dataset property values
        """
        xml_content = read_file_content(
            os.path.join(TestParsedDcat.test_dir + 'metadata/dcat/dcat.xml'))
        pead = ParsedDcat(xml_content.encode('utf-8'))
        titles = pead.get_distribution_property_values()
        print(titles)


if __name__ == '__main__':
    unittest.main()
