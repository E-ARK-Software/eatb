#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import unittest

from eatb import root_dir
from eatb.metadata.mets.metsutil import get_package_mets_files_from_basedir, get_mets_obj_id, \
    get_mets_objids_from_basedir


class METSUtilTest(unittest.TestCase):

    def test_get_package_mets_files_in_directory(self):
        """
        Must return METS.xml files of information package directories contained in a given directory
        """
        mets_files = get_package_mets_files_from_basedir(os.path.join(root_dir, 'tests/test_resources/metadata/mets/'))
        self.assertTrue(len(mets_files) > 0)
        for mets_file in mets_files:
            self.assertTrue(mets_file.endswith("METS.xml"))

    def test_get_identifier_from_mets(self):
        """
        Must return METS.xml files of information package directories contained in a given directory
        """
        mets_file = os.path.join(root_dir, 'tests/test_resources/metadata/mets/METS.xml')
        self.assertEqual("996ed635-3e13-4ee5-8e5b-e9661e1d9a93", get_mets_obj_id(mets_file))


if __name__ == '__main__':
    unittest.main()
