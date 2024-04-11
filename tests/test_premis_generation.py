#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

from lxml import etree

from eatb import ROOT
from eatb.metadata.premis_generator import PremisGenerator
from eatb.utils import randomutils


class TestPremisCreation(unittest.TestCase):
    test_ip = "eark-ip"
    test_ip_mig = "eark-ip-mig"
    test_source_directory = os.path.join(ROOT + '/tests/test_resources/')
    temp_working_dir = os.path.join(ROOT, "tmp/tmp-%s" % randomutils.randomword(10))
    tmp_ip_dir = os.path.join(temp_working_dir, test_ip)
    tmp_ip_dir_mig = os.path.join(temp_working_dir, test_ip_mig)

    test_ip_dir = os.path.join(test_source_directory, test_ip)
    test_ip_dir_mig = os.path.join(test_source_directory, test_ip_mig)

    premis_file_path = os.path.join(temp_working_dir, test_ip, './metadata/preservation/premis.xml')

    premis_schema_file = os.path.join(ROOT, 'tests/test_resources/schemas/premis-v3-0.xsd')

    @classmethod
    def setUpClass(cls):
        shutil.copytree(TestPremisCreation.test_ip_dir, TestPremisCreation.tmp_ip_dir)
        shutil.copytree(TestPremisCreation.test_ip_dir_mig, TestPremisCreation.tmp_ip_dir_mig)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestPremisCreation.temp_working_dir)
        pass

    def validate_xml(self, file, premis_schema_file):
        validation_errors = []
        xmlschema = etree.XMLSchema(etree.parse(premis_schema_file))
        try:
            xmlschema.assertValid(etree.parse(file))
            print('Validation result: %s' % xmlschema.validate(etree.parse(file)))
        except etree.XMLSyntaxError as e:
            validation_errors.append(str(e))
        if len(validation_errors) > 0:
            print(validation_errors)

    def test_create_premis(self):

        premisgen = PremisGenerator(TestPremisCreation.tmp_ip_dir)
        premisgen.createPremis()
        self.validate_xml(TestPremisCreation.premis_file_path, TestPremisCreation.premis_schema_file)

    def test_add_premis_event(self):
        premisgen = PremisGenerator(TestPremisCreation.tmp_ip_dir_mig)

        premisinfo = {'outcome': 'success',
                      'task_name': 'SIPValidation',
                      'event_type': 'SIP validation',
                      'linked_object': 'this-is-a-package-id'}

        premisgen.addEvent('metadata/preservation/premis.xml', premisinfo)

        premis = '%s/metadata/preservation/premis.xml' % TestPremisCreation.tmp_ip_dir_mig

        self.validate_xml(premis, TestPremisCreation.premis_schema_file)


if __name__ == '__main__':
    unittest.main()
