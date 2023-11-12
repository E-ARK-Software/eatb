#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest
import re
import io

from lxml import isoschematron
from lxml import etree

from eatb import ROOT
from eatb.utils.fileutils import rec_find_files
from eatb.utils.randomutils import randomword


def get_rule(lines, rule_id):
    rules_ids = [rule_id]
    n_header_lines = 5
    rule = lines[:n_header_lines] # add schema and namespaces
    rule_found = False
    # select all patterns with matching id
    for line in lines[n_header_lines:]:
        if not rule_found:
            # look for beginning of pattern/rule
            match = re.search('pattern id="CSIP(.+?)"', line)
            if match:
                current_id = int(match.group(1))
                if current_id in rules_ids:
                    # select pattern
                    rule.append(line)
                    rule_found = True
                # else ignore pattern
            # else is not the beginning of a pattern
        elif '</pattern>' in line:
            # pattern/rule is over
            rule.append(line)
            rule_found = False
        else:
            rule.append(line)
    rule.append('</schema>\n')
    res = '\n'.join(rule)
    return res


def validate(rules_lines, xml_file, rule_id):
    # Parse rules
    single_rule = io.StringIO(get_rule(rules_lines, rule_id))
    parsed_single_rule = etree.parse(single_rule)
    schematron = isoschematron.Schematron(parsed_single_rule, store_report=True)

    # Parse XML to validate
    parsed_xml_file = etree.parse(xml_file)
    validation_response = schematron.validate(parsed_xml_file)
    report = schematron.validation_report
    return validation_response, report


class TestUtils(unittest.TestCase):
    temp_extract_dir = '/tmp/backend-utils-' + randomword(10)

    @classmethod
    def setUpClass(cls):
        tests_dir = os.path.join(ROOT, 'tests/test_resources/package')
        shutil.copytree(tests_dir, TestUtils.temp_extract_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestUtils.temp_extract_dir)
        #pass

    def test_recursive_find_files_in_dir(self):

        def check_paths(retrieved_file_list, expected_paths):
            for retrieved_path in retrieved_file_list:
                self.assertTrue(retrieved_path in expected_paths,
                                "Retrieved path %s not in expected list" % retrieved_path)
            for expected_path in expected_paths:
                self.assertTrue(expected_path in retrieved_file_list,
                                "Expected path %s not in retrieved list" % expected_path)

        def check_excluded(retrieved_file_list, excluded_paths):
            for excluded_path in excluded_paths:
                self.assertTrue(excluded_path not in retrieved_file_list,
                                "Excluded path %s appears in retrieved files list" % excluded_path)

        flist = list(rec_find_files(TestUtils.temp_extract_dir, include_files_rgxs=None, exclude_dirsfiles_rgxs=None))

        self.assertEqual(len(flist), 6, "Number of files not as expected")
        check_paths(flist, expected_paths = (
            os.path.join(TestUtils.temp_extract_dir, 'first_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/second_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/screen.png'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/second_level.csv'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/subsubfolder/third_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/subsubfolder/subsubsubfolder/fourth_level.txt'),
        ))
        with self.assertRaises(AssertionError):
            list(rec_find_files(TestUtils.temp_extract_dir, include_files_rgxs="*.txt", exclude_dirsfiles_rgxs=None))

        flist = list(rec_find_files(TestUtils.temp_extract_dir, include_files_rgxs=[r'.*\.txt$'], exclude_dirsfiles_rgxs=None))
        check_paths(flist, expected_paths = (
            os.path.join(TestUtils.temp_extract_dir, 'first_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/second_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/subsubfolder/third_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/subsubfolder/subsubsubfolder/fourth_level.txt'),
        ))
        check_excluded(flist, excluded_paths=(
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/screen.png'),
        ))
        flist = list(rec_find_files(TestUtils.temp_extract_dir, include_files_rgxs=[r'.*\.txt$', r'.*\.csv$'], exclude_dirsfiles_rgxs=None))
        check_paths(flist, expected_paths = (
            os.path.join(TestUtils.temp_extract_dir, 'first_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/second_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/second_level.csv'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/subsubfolder/third_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/subsubfolder/subsubsubfolder/fourth_level.txt'),
        ))
        check_excluded(flist, excluded_paths=(
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/screen.png'),
        ))
        flist = list(rec_find_files(TestUtils.temp_extract_dir, include_files_rgxs=[r'.*\.txt$', r'.*\.csv$'],
                                     exclude_dirsfiles_rgxs=[r'.*/subfolder.*']))
        check_paths(flist, expected_paths=(
            os.path.join(TestUtils.temp_extract_dir, 'first_level.txt'),
        ))

        flist = list(rec_find_files(TestUtils.temp_extract_dir, include_files_rgxs=[r'.*\.txt$'],
                                    exclude_dirsfiles_rgxs=[r'.*first_level.txt$']))
        check_paths(flist, expected_paths=(
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/second_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/subsubfolder/third_level.txt'),
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/subsubfolder/subsubsubfolder/fourth_level.txt'),
        ))

        flist = list(rec_find_files(TestUtils.temp_extract_dir, include_files_rgxs=[r'.*\.txt$'],
                                    exclude_dirsfiles_rgxs=[r'.*first_level.txt$', r'.*/subsubfolder.*']))
        check_paths(flist, expected_paths=(
            os.path.join(TestUtils.temp_extract_dir, 'subfolder/second_level.txt'),
        ))


if __name__ == '__main__':
    unittest.main()
