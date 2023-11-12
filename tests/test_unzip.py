#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

from eatb import ROOT
from eatb.packaging import ZipContainer
from eatb.utils.randomutils import randomword


class TestExtraction(unittest.TestCase):

    test_resources_dir = os.path.join(ROOT, 'tests/test_resources')
    temp_extract_dir = '/tmp/backend-unzip-' + randomword(10)

    @classmethod
    def setUpClass(cls):
        os.makedirs(TestExtraction.temp_extract_dir)
        zip_container_test_resource_path = os.path.join(TestExtraction.test_resources_dir, "package.zip")
        shutil.copy(zip_container_test_resource_path, TestExtraction.temp_extract_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestExtraction.temp_extract_dir)
        pass

    def test_extract_sip(self):
        print("Extracting to %s" % self.temp_extract_dir)
        zip_container_file_path = os.path.join(TestExtraction.temp_extract_dir, "package.zip")
        container_folder = "package"
        zip_container = ZipContainer(zip_container_file_path)
        success = zip_container.unzip(TestExtraction.temp_extract_dir)
        self.assertTrue(success)
        cpt = sum([len(files) for r, d, files in os.walk(TestExtraction.temp_extract_dir)])
        self.assertEqual(cpt, 3, "Number of extracted files not as expected")
        files_to_check = (
            os.path.join(TestExtraction.temp_extract_dir, container_folder, './first_level.txt'),
            os.path.join(TestExtraction.temp_extract_dir, container_folder, './subfolder/second_level.txt'),
        )
        for file in files_to_check:
            self.assertTrue(os.path.isfile(file), "File %s not found in extracted directory" + file)


if __name__ == '__main__':
    unittest.main()
