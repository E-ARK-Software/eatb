#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

from pairtree import ObjectNotFoundException

from eatb import ROOT
from eatb.pairtree_storage import PairtreeStorage
from eatb.utils import randomutils

source_dir = os.path.join(ROOT, 'tests/test_resources/storage-test/')
package_file = "xyz.tar"
package_file_path = os.path.join(source_dir, package_file)
repository_storage_dir = '/tmp/temp-' + randomutils.randomword(10)
test_repo = os.path.join(ROOT, 'tests/test_resources/test-repo/')


class TestPairtreeStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(repository_storage_dir):
            os.makedirs(repository_storage_dir)
        shutil.copy(os.path.join(test_repo, "pairtree_version0_1"), repository_storage_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(repository_storage_dir)

    def test_identifier_object_exists(self):
        pts = PairtreeStorage(test_repo)
        existing_identifier = "bar"
        non_existing_identifier = "foo"
        existing_identifier_exists = pts.identifier_object_exists(existing_identifier)
        non_existing_identifier_exists = pts.identifier_object_exists(non_existing_identifier)
        self.assertEqual(existing_identifier_exists, True)
        self.assertEqual(non_existing_identifier_exists, False)

    def test_version_exists(self):
        pts = PairtreeStorage(test_repo)
        identifier = "bar"
        self.assertEqual(pts.identifier_version_object_exists(identifier, 3),False)
        self.assertEqual(pts.identifier_version_object_exists(identifier, 2),True)

    def test_next_version(self):
        pts = PairtreeStorage(test_repo)
        identifier = "bar"
        self.assertEqual("v00003", pts._next_version(identifier))

    def test_curr_version(self):
        pts = PairtreeStorage(test_repo)
        identifier = "bar"
        self.assertEqual("v00002", pts.curr_version(identifier))

    def test_store(self):
        pts = PairtreeStorage(repository_storage_dir)
        pts.store("xyz", package_file_path)
        self.assertEqual(1, pts.curr_version_num("xyz"))
        pts.store("xyz", package_file_path)
        self.assertEqual(2, pts.curr_version_num("xyz"))

    def test_get_object_path(self):
        pts = PairtreeStorage(test_repo)
        expected = os.path.join(test_repo, "pairtree_root/ba/r/data/v00002")
        print(expected)
        actual = pts.get_object_path("bar")
        print(actual)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
