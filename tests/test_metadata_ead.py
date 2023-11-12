#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from eatb import ROOT
from eatb.metadata.parsed_ead import ParsedEad


class TestParsedEad(unittest.TestCase):
    test_dir = os.path.join(ROOT, 'tests/test_resources/EAD-test/')

    def test_get_root_element(self):
        """
        Must not validate if the files listed in the EAD file does not match the actual file size
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example1.xml')
        actual = pead.ead_tree.getroot().tag
        self.assertEqual(actual, "{http://ead3.archivists.org/schema/}ead", "Root tag 'ead' not found")

    def test_get_dao_elements(self):
        """
        Test get dao elements
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example1.xml')
        dao_elements = pead.get_dao_elements()
        self.assertIsNotNone(dao_elements, "DAO elements must not be None")
        self.assertEqual(len(dao_elements), 2, "DAO elements list must have two DAO element")

    def test_first_metadata_value_in_ancestry_path(self):
        """
        Test get closest unittitle element value (c04)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example1.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("Record - Adams-Ayers", pead._first_md_val_ancpath(dao_elm, "unittitle"))

    def test_first_metadata_value_in_ancestry_path_unitdatestructured(self):
        """
        Test get closest unittitle element value (c04)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example1.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("22.04.2016", pead._first_md_val_ancpath(dao_elm, "unitdatestructured", "ead:datesingle"))

    def test_first_metadata_value_in_ancestry_path_unitdatestructured_range(self):
        """
        Test get closest unittitle element value (c04)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example6.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("22.04.2016", pead._first_md_val_ancpath(dao_elm, "unitdatestructured", "ead:daterange/ead:fromdate"))
            self.assertEqual("28.04.2016", pead._first_md_val_ancpath(dao_elm, "unitdatestructured", "ead:daterange/ead:todate"))

    def test_first_metadata_value_in_ancestry_path_origination(self):
        """
        Test get closest unittitle element value (c04)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example5.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("Test Agency", pead._first_md_val_ancpath(dao_elm, "origination", "ead:corpname/ead:part"))

    def test_first_metadata_value_in_ancestry_path_origination_xpath(self):
        """
        Test get closest unittitle element value (text access xpath)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example5.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("Test Agency", pead._first_md_val_ancpath(dao_elm, "origination", text_accessor="*/ead:part"))

    def test_first_metadata_value_in_ancestry_path_c03(self):
        """
        Test get closest unittitle element value (c03)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example2.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("Adams-Ayers", pead._first_md_val_ancpath(dao_elm, "unittitle"))

    def test_first_metadata_value_in_ancestry_path_c02(self):
        """
        Test get closest unittitle element value (c02)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example3.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("Incoming Correspondence", pead._first_md_val_ancpath(dao_elm, "unittitle"))

    def test_first_metadata_value_in_ancestry_path_c01(self):
        """
        Test get closest unittitle element value (c01)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example4.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("Correspondence", pead._first_md_val_ancpath(dao_elm, "unittitle"))

    def test_dao_title_tuples(self):
        """
        Test dao tuples
        """
        parsed_ead = TestParsedEad.test_dir
        ead_file_path = TestParsedEad.test_dir + 'metadata/descriptive/EAD-example1.xml'
        pead = ParsedEad(parsed_ead, ead_file_path)
        md_tag = "unittitle"
        res = pead.dao_path_mdval_tuples(md_tag)
        self.assertEqual("representations/rep1/data/Example1.docx", res[0]['path'])
        self.assertEqual("representations/rep2/data/Example1.pdf", res[1]['path'])
        self.assertEqual("Record - Adams-Ayers", res[0]['mdvalue'])
        self.assertEqual("Record - Adams-Ayers", res[1]['mdvalue'])

    def test_dao_unitdatestructured_datevalue_subelement(self):
        """
        Test dao tuples
        """
        parsed_ead = TestParsedEad.test_dir
        ead_file_path = TestParsedEad.test_dir + 'metadata/descriptive/EAD-example1.xml'
        pead = ParsedEad(parsed_ead, ead_file_path)
        md_tag = "unitdatestructured"
        res = pead.dao_path_mdval_tuples(md_tag, "ead:datesingle")
        self.assertEqual("22.04.2016", res[0]['mdvalue'])

    def test_c_level(self):
        """
        Test get closest unittitle element value (c01)
        """
        pead = ParsedEad(TestParsedEad.test_dir, TestParsedEad.test_dir + 'metadata/descriptive/EAD-example1.xml')
        dao_elements = pead.get_dao_elements()
        for dao_elm in dao_elements:
            self.assertEqual("item", pead._first_md_val_ancpath(dao_elm, "[Cc][0,1][0-9]", "level", True))

    def test_dao_clevel_attribute_value(self):
        """
        Test dao tuples
        """
        parsed_ead = TestParsedEad.test_dir
        ead_file_path = TestParsedEad.test_dir + 'metadata/descriptive/EAD-example1.xml'
        pead = ParsedEad(parsed_ead, ead_file_path)
        md_tag = "[Cc][0,1][0-9]"
        res = pead.dao_path_mdval_tuples(md_tag, "level", True)
        self.assertEqual("item", res[0]['mdvalue'])



if __name__ == '__main__':
    unittest.main()
