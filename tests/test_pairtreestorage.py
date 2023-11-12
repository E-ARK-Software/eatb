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
        pts.store("xyz", os.path.join(source_dir))
        self.assertEqual(0, pts.curr_version_num("xyz"))
        pts.store("xyz", os.path.join(source_dir))
        self.assertEqual(1, pts.curr_version_num("xyz"))

    def test_get_object_path(self):
        pts = PairtreeStorage(test_repo)
        expected = os.path.join(test_repo, "pairtree_root/ba/r/data/v00002/content/bar_v00002_b00001")
        actual = pts.get_object_path("bar")
        self.assertEqual(expected, actual)

    def test_read_tar_file_entry_as_chunks(self):
        pts = PairtreeStorage(test_repo)
        identifier = "bar"
        entry = "739f9c5f-c402-42af-a18b-3d0bdc4e8751/METS.xml"
        chunked_tar_entry_reader = pts.get_chunked_tar_entry_reader(identifier)
        try:
            chunks = chunked_tar_entry_reader.chunks(entry)
            content = ''.join([chunk.decode('utf-8') for chunk in chunks])
            self.assertTrue(content.startswith("<?xml"))
        except KeyError:
            raise ObjectNotFoundException("Entry '%s' not found in package '%s'" % (entry, identifier))
        finally:
            chunked_tar_entry_reader.close()


if __name__ == '__main__':
    unittest.main()
