#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import json
import shutil

from eatb.packaging.manifest import ManifestCreation
from eatb.utils import randomutils

import unittest

from eatb import root_dir


class TestManifestCreation(unittest.TestCase):
    test_asset = os.path.join(root_dir + '/tests/test_resources/test-repo')
    temp_working_dir = root_dir + '/tmp/temp-aip-dir-' + randomutils.randomword(10) + "/"
    manifest_file = os.path.join(temp_working_dir, './manifest.mf')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestManifestCreation.temp_working_dir)

    def test_create_manifest(self):
        manifest_creation = ManifestCreation(TestManifestCreation.temp_working_dir)
        manifest_creation.create_manifest(self.test_asset, self.manifest_file)
        self.assertTrue(os.path.isfile(self.manifest_file), "File not found in working directory")
        with open(TestManifestCreation.manifest_file, 'r') as json_file:
            json_manifest = json.load(json_file)
        self.assertEqual(67, len(json_manifest))


if __name__ == '__main__':
    unittest.main()
