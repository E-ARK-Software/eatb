#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from eatb import ROOT
from eatb.metadata.mets import get_package_mets_files_from_basedir, get_mets_obj_id


class METSUtilTest(unittest.TestCase):

    def test_get_package_mets_files_in_directory(self):
        """
        Must return METS.xml files of information package directories contained in a given directory
        """
        mets_files = get_package_mets_files_from_basedir(os.path.join(ROOT, 'tests/test_resources/metadata/mets/'))
        self.assertTrue(len(mets_files) > 0)
        for mets_file in mets_files:
            self.assertTrue(mets_file.endswith("METS.xml"))

    def test_get_identifier_from_mets(self):
        """
        Must return METS.xml files of information package directories contained in a given directory
        """
        mets_file = os.path.join(ROOT, 'tests/test_resources/metadata/mets/METS.xml')
        self.assertEqual("996ed635-3e13-4ee5-8e5b-e9661e1d9a93", get_mets_obj_id(mets_file))


if __name__ == '__main__':
    unittest.main()
