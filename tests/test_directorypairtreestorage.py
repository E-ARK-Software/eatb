import shutil

import os
import tarfile
import tempfile
import unittest

from eatb import ROOT
from eatb.storage.directorypairtreestorage import DirectoryPairtreeStorage

class TestDirectoryPairtreeStorage(unittest.TestCase):

    source_dir = os.path.join(ROOT, 'tests/test_resources/storage-test')
    test_repo_resources = os.path.join(ROOT, 'tests/test_resources/test-repo/')
    tmp_test_directory = tempfile.mkdtemp()
    tmp_test_repo = os.path.join(tmp_test_directory, "test-repo")

    @classmethod
    def setUpClass(cls):
        # os.makedirs(TestDirectoryPairtreeStorage.tmp_test_directory)
        shutil.copytree(TestDirectoryPairtreeStorage.test_repo_resources,
                        os.path.join(TestDirectoryPairtreeStorage.tmp_test_repo))

    @classmethod
    def tearDownClass(cls):
        #shutil.rmtree(TestDirectoryPairtreeStorage.tmp_test_directory)
        pass

    def test_identifier_object_exists(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        existing_identifier = "bar"
        nonexisting_identifier = "xyz"
        self.assertEqual(pts.identifier_object_exists(existing_identifier), True)
        self.assertEqual(pts.identifier_object_exists(nonexisting_identifier), False)

    def test_version_exists(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        identifier = "bar"
        version1_exists = pts.identifier_version_object_exists(identifier, 1)
        self.assertEqual(version1_exists, True)
        version2_exists = pts.identifier_version_object_exists(identifier, 2)
        self.assertEqual(version2_exists, True)
        version3_exists = pts.identifier_version_object_exists(identifier, 3)
        self.assertEqual(version3_exists, False)

    def test_next_version(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        identifier = "bar"
        next_version_dirname = pts._next_version(identifier)
        self.assertEqual("00003", next_version_dirname)

    def test_curr_version(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        identifier = "bar"
        self.assertEqual("00002", pts.curr_version(identifier))

    def test_store(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        pts.store("minimal_IP_with_schemas", TestDirectoryPairtreeStorage.source_dir)
        self.assertEqual(1, pts.curr_version_num("minimal_IP_with_schemas"))
        pts.store("minimal_IP_with_schemas", TestDirectoryPairtreeStorage.source_dir)
        self.assertEqual(2, pts.curr_version_num("minimal_IP_with_schemas"))

    def test_get_object_path(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        expected = os.path.join(TestDirectoryPairtreeStorage.tmp_test_repo, "pairtree_root/ba/r/data/00002/bar")
        actual = pts.get_object_path("bar")
        self.assertEqual(expected, actual)

    def test_get_object_item_stream(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        tar_file_path = pts.get_tar_file_path("bar", "default")
        self.assertTrue(os.path.exists(tar_file_path))
        tar_file = tarfile.open(tar_file_path, 'r')
        content = pts.get_object_item_stream("bar", "default", "default/data/example.txt", tar_file=tar_file)
        content_chunk = next(content)
        content_chunk_text = content_chunk.decode('utf-8')
        self.assertTrue(content_chunk_text.startswith("text file content"))
        tar_file.close()

    def test_store_versions_single_package(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        source_dir_opq = os.path.join(ROOT, 'tests/test_resources/storage-test-opq/./')
        version = pts.store("opq", source_dir_opq)
        self.assertEqual("00001", version)
        tar_file_path = pts.get_tar_file_path("opq")
        self.assertTrue(os.path.exists(tar_file_path))
        version = pts.store("opq", source_dir_opq)
        self.assertEqual("00002", version)
        tar_file_path = pts.get_tar_file_path("opq")
        self.assertTrue(os.path.exists(tar_file_path))

    def test_store_versions_packaged_distributions(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo)
        version = pts.store("xyz", TestDirectoryPairtreeStorage.source_dir, single_package=False)
        self.assertEqual("00001", version)
        tar_file_path = pts.get_tar_file_path("xyz")
        self.assertTrue(os.path.exists(tar_file_path))

    def test_store_versions_packaged_distribution_versions(self):
        pts = DirectoryPairtreeStorage(TestDirectoryPairtreeStorage.tmp_test_repo,
                                       representations_directory="distributions")
        # store first version
        abc1_src_dir = os.path.join(ROOT, 'tests/test_resources/distributionpackages/abc1')
        version = pts.store("abc", abc1_src_dir, single_package=False)
        self.assertEqual("00001", version)
        distr_tar_file_path = pts.get_tar_file_path("abc", "default")
        self.assertTrue(os.path.exists(distr_tar_file_path))
        tar_file = tarfile.open(distr_tar_file_path, 'r')
        content = pts.get_object_item_stream(identifier="bar",
                                             entry="default/data/example.txt", representation_label="default",
                                             tar_file=tar_file)

        # read text file contained in the distribution
        content_chunk = next(content)
        content_chunk_text = content_chunk.decode('utf-8')
        self.assertTrue(content_chunk_text.startswith("text file content"))
        tar_file.close()

        # store second version (packaged distribution differs from first one)
        abc2_src_dir = os.path.join(ROOT, 'tests/test_resources/distributionpackages/abc2')
        version = pts.store("abc", abc2_src_dir, single_package=False)
        self.assertEqual("00002", version)


if __name__ == '__main__':
    unittest.main()
    #dpts = DirectoryPairtreeStorage(config_path_storage)
    #dpts.store_working_directory("922daee4-5beb-49c3-96d4-d4f67670c741", "ait:8e93be0e7f9ba763784c96bc3974a45b545f060e")
    #trigger_new_version("13d90477-a9f6-4dd9-99fe-c7fb9a0ae0b1", "ait:874e5606bd9f39529adb5d84ce52b3cb06ae91bc")
