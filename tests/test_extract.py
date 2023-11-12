#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import shutil
import unittest

from eatb import ROOT
from eatb.utils import randomutils
from eatb.packaging import PackagedContainer


class TestExtract(unittest.TestCase):
    test_dir = os.path.join(ROOT, 'tests/test_resources/')
    temp_extract_dir = '/tmp/temp-' + randomutils.randomword(10)

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(TestExtract.temp_extract_dir):
            os.makedirs(TestExtract.temp_extract_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestExtract.temp_extract_dir)
        pass

    @staticmethod
    def reset_test_dir():
        shutil.rmtree(TestExtract.temp_extract_dir)
        os.makedirs(TestExtract.temp_extract_dir)

    def assert_extract(self, package_file):
        package_file_path = os.path.join(TestExtract.test_dir, package_file)
        packaged_container = PackagedContainer.factory(package_file_path)
        packaged_container.extract(TestExtract.temp_extract_dir)
        # must be 8 extracted files
        item_counts = [(len(r), len(d), len(files)) for r, d, files in os.walk(TestExtract.temp_extract_dir)]
        sum_files = sum(ic[2] for ic in item_counts)
        self.assertEqual(sum_files, 2, "Number of extracted files not as expected")
        sum_directories = sum(ic[1] for ic in item_counts)
        self.assertEqual(sum_directories, 2, "Number of extracted directories not as expected")
        files_to_check = (
            os.path.join(TestExtract.temp_extract_dir, 'package/first_level.txt'),
            os.path.join(TestExtract.temp_extract_dir, 'package/subfolder/second_level.txt'),
        )
        for file in files_to_check:
            self.assertTrue(os.path.isfile(file), "File %s not found in extracted directory" + file)
        TestExtract.reset_test_dir()

    def test_extract_zip(self):
        self.assert_extract("package.zip")

    def test_extract_tar(self):
        self.assert_extract("package.tar.gz")


if __name__ == '__main__':
    unittest.main()
