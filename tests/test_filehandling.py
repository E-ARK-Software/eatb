#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import unittest

from eatb import ROOT
from eatb.utils.fileutils import remove_protocol, strip_prefixes, get_sub_path_from_relative_path


class TestPathFunctions(unittest.TestCase):

    def test_remove_protocol(self):
        self.assertEqual('/test', remove_protocol("file:///test"))

    def test_strip_prefixes_from_path_singlefile(self):
        full_path = '/to/be/stripped/someotherpart/file.txt'
        path_part1 = '/to/be/stripped'
        path_part2 = 'someotherpart'
        self.assertEqual('file.txt', strip_prefixes(full_path, path_part1, path_part2))

    def test_strip_prefixes_from_path_file_in_subdir(self):
        full_path = '/to/be/stripped/someotherpart/sub/dir/file.txt'
        path_part1 = '/to/be/stripped'
        path_part2 = 'someotherpart'
        self.assertEqual('sub/dir/file.txt', strip_prefixes(full_path, path_part1, path_part2))

    def test_strip_single_prefix_from_path(self):
        full_path = '/to/be/stripped/someotherpart/file.txt'
        path_part = '/to/be/stripped'
        self.assertEqual('someotherpart/file.txt', strip_prefixes(full_path, path_part))

    def test_package_path_from_relative_path(self):
        test_ip = "eark-ip"
        test_source_directory = os.path.join(ROOT + '/tests/test_resources/')

        test_ip_root = os.path.join(test_source_directory, test_ip)

        containing_file_path = os.path.join(test_ip_root, 'metadata/descriptive/EAD.xml')

        relative_path = '../../submission/metadata/descriptive/EAD.xml'
        self.assertEqual("submission/metadata/descriptive/EAD.xml",
                         get_sub_path_from_relative_path(test_ip_root, containing_file_path, relative_path))


if __name__ == '__main__':
    unittest.main()
