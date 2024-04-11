#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from lxml import etree

import eatb.metadata.premis
from eatb import ROOT
from eatb.metadata.parsed_premis import ParsedPremis
from eatb.utils.xmlutils import pretty_xml_string
from eatb.csip_validation import XmlValidation

premis_skeleton = os.path.join(ROOT, 'tests/test_resources/metadata/premis/PREMIS_skeleton.xml')
premis_schema_file = os.path.join(ROOT, 'tests/test_resources/schemas/premis-v3-0.xsd')


class TestPremisManipulate(unittest.TestCase):


    def test_premis_manipulate(self):
        with open(os.path.join(ROOT, premis_skeleton), 'r') as premis_file:
            self.my_premis = ParsedPremis(premis_file)
            self.my_premis.add_agent('Aip2Dip')
            self.my_premis.add_event('Migration01', 'success', 'Aip2Dip',
                                           'linking_agent')
            self.my_premis.add_object('file.txt')
            premis_xml = pretty_xml_string(self.my_premis.to_string())
            print(premis_xml)
            xmlval = XmlValidation()
            parsed_xml = etree.fromstring(premis_xml)
            parsed_schema = etree.parse(premis_schema_file)
            validation_result = xmlval.validate_XML(parsed_xml,parsed_schema)
            print(validation_result)


if __name__ == '__main__':
    unittest.main()
