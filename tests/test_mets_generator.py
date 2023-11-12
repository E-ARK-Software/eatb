#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

from eatb import ROOT
from eatb.metadata.parsed_mets import ParsedMets
from eatb.utils import randomutils
from eatb.metadata.mets_generator import MetsGenerator


class TestMetsCreation(unittest.TestCase):

    test_ip = "eark-ip"
    test_source_directory = os.path.join(ROOT + '/tests/test_resources/')
    temp_working_dir = os.path.join(ROOT, "tmp/tmp-%s" % randomutils.randomword(10))
    tmp_ip_dir = os.path.join(temp_working_dir, test_ip)

    test_ip_dir = os.path.join(test_source_directory, test_ip)

    mets_file_path = os.path.join(temp_working_dir, test_ip, 'METS.xml')

    @classmethod
    def setUpClass(cls):
        shutil.copytree(TestMetsCreation.test_ip_dir, TestMetsCreation.tmp_ip_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestMetsCreation.temp_working_dir)
        pass

    @unittest.skip("Currently throws a KeyError:'data' error @{}". \
        format("eatb/metadata/mets/mets.py:446"))
    def testCreateMets(self):
        metsgen = MetsGenerator(TestMetsCreation.test_ip_dir)
        mets_data = {'packageid': '996ed635-3e13-4ee5-8e5b-e9661e1d9a93',
                     'type': 'AIP', 'schemas': 'schemas', 'parent': None}
        metsgen.createMets(mets_data, TestMetsCreation.mets_file_path)
        self.assertTrue(os.path.exists(TestMetsCreation.mets_file_path))

        pm = ParsedMets(TestMetsCreation.test_ip_dir)
        pm.load_mets(TestMetsCreation.mets_file_path)

        obj_id = pm.get_obj_id()
        self.assertEqual("996ed635-3e13-4ee5-8e5b-e9661e1d9a93", obj_id)


if __name__ == '__main__':
    unittest.main()
