import shutil

import os
import unittest

from eatb import root_dir
from eatb.storage.directorypairtreestorage import DirectoryPairtreeStorage
from eatb.utils import randomutils


class TestDirectoryPairtreeStorage(unittest.TestCase):
    source_dir = root_dir + 'tests/test_resources/package'
    test_repo_resources = root_dir + 'tests/test_resources/test-repo/'
    test_directory = root_dir + '/tmp/temp-' + randomutils.randomword(10)
    test_repo = os.path.join(test_directory, "test-repo")

    @classmethod
    def setUpClass(cls):
        os.makedirs(TestDirectoryPairtreeStorage.test_directory)
        shutil.copytree(TestDirectoryPairtreeStorage.test_repo_resources, os.path.join(TestDirectoryPairtreeStorage.test_repo))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestDirectoryPairtreeStorage.test_directory)
        pass

    def test_identifier_object_exists(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.test_repo)
        existing_identifier = "bar"
        nonexisting_identifier = "xyz"
        self.assertEquals(pts.identifier_object_exists(existing_identifier), True)
        self.assertEquals(pts.identifier_object_exists(nonexisting_identifier), False)

    def test_version_exists(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.test_repo)
        identifier = "bar"
        self.assertEquals(pts.identifier_version_object_exists(identifier, 2),False)
        self.assertEquals(pts.identifier_version_object_exists(identifier, 1),True)

    def test_next_version(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.test_repo)
        identifier = "bar"
        self.assertEquals("00002", pts._next_version(identifier))

    def test_curr_version(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.test_repo)
        identifier = "bar"
        self.assertEquals("00001", pts.curr_version(identifier))

    def test_store(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.test_repo)
        pts.store("foo", TestDirectoryPairtreeStorage.source_dir)
        self.assertEqual(1, pts.curr_version_num("foo"))
        pts.store("foo", TestDirectoryPairtreeStorage.source_dir)
        self.assertEqual(2, pts.curr_version_num("foo"))

    def test_get_object_path(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.test_repo)
        expected = os.path.join(TestDirectoryPairtreeStorage.test_repo, "pairtree_root/ba/r/data/00001/bar")
        actual = pts.get_object_path("bar")
        self.assertEqual(expected, actual)

    def test_get_object_item_stream(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.test_repo)
        content = pts.get_object_item_stream("bar", "default", "default/data/example.txt")
        content_chunk = content.next()
        self.assertTrue(content_chunk.startswith("Example"))

    def test_store_dma(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.test_repo)
        pts.store("ait:474cd4162c31708b42ebbd21bcabacd4fce6665a", TestDirectoryPairtreeStorage.source_dir)
        content = pts.get_object_item_stream("ait:474cd4162c31708b42ebbd21bcabacd4fce6665a", "default", "default/data/example.txt")
        content_chunk = content.next()
        self.assertTrue(content_chunk.startswith("Example"))
        self.assertEqual(1, pts.curr_version_num("ait:474cd4162c31708b42ebbd21bcabacd4fce6665a"))
        pts.store("ait:474cd4162c31708b42ebbd21bcabacd4fce6665a", TestDirectoryPairtreeStorage.source_dir)
        self.assertEqual(2, pts.curr_version_num("ait:474cd4162c31708b42ebbd21bcabacd4fce6665a"))


if __name__ == '__main__':
    unittest.main()
    #dpts = DirectoryPairtreeStorage(config_path_storage)
    #dpts.store_working_directory("922daee4-5beb-49c3-96d4-d4f67670c741", "ait:8e93be0e7f9ba763784c96bc3974a45b545f060e")
    #trigger_new_version("13d90477-a9f6-4dd9-99fe-c7fb9a0ae0b1", "ait:874e5606bd9f39529adb5d84ce52b3cb06ae91bc")
