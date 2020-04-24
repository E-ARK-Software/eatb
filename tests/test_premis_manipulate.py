#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from lxml import etree

from eatb import ROOT
from eatb.metadata.premis.PremisManipulate import Premis
from eatb.xml.xmlutils import pretty_xml_string
from eatb.xml.xmlvalidation import XmlValidation

class TestPremisManipulate(unittest.TestCase):

    premis_skeleton = 'tests/test_resources/metadata/premis/PREMIS_skeleton.xml'
    premis_schema_file = os.path.join(ROOT, 'tests/test_resources/schemas/premis-v2-2.xsd')

    def test_premis_manipulate(self):
        with open(os.path.join(ROOT, TestPremisManipulate.premis_skeleton), 'r') as premis_file:
            self.my_premis = Premis(premis_file)
            self.my_premis.add_agent('Aip2Dip')
            self.my_premis.add_event('Migration01', 'success', 'Aip2Dip')
            self.my_premis.add_object('file.txt')
            premis_xml = pretty_xml_string(self.my_premis.to_string())
            print(premis_xml)
            xmlval = XmlValidation()
            parsed_xml = etree.fromstring(premis_xml)
            parsed_schema = etree.parse(TestPremisManipulate.premis_schema_file)
            validation_result = xmlval.validate_XML(parsed_xml,parsed_schema)
            print(validation_result)


if __name__ == '__main__':
    unittest.main()
