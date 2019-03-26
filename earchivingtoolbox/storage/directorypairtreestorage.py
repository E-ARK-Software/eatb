# coding=UTF-8
import fnmatch
import json
import logging
from conduitcore.filesystem.chunked import FileBinaryDataChunks

from conduitcore.filesystem.chunkedtarentryreader import ChunkedTarEntryReader
from conduitcore.filesystem.fsinfo import fsize
from conduitcore.fixity.ChecksumFile import ChecksumFile
from conduitcore.fixity.tasklib import check_transfer
from conduitcore.utils.fileutils import mkdir_p, get_immediate_subdirectories, copy_file_with_base_directory, \
    rec_find_files
from conduitcore.utils.pathutils import uri_to_safe_filename
from conduittasks.ip_state import IpState

logger = logging.getLogger(__name__)

import shutil

import os
import os.path
import unittest
import ntpath
import tarfile
from conduitcore.utils import randomutils

from config.configuration import root_dir, config_path_work, representations_directory
from itertools import groupby
from config.configuration import config_path_storage
from pairtree import PairtreeStorageFactory, ObjectNotFoundException

VersionDirFormat = '%05d'


def default_reporter(percent):
    print("\rProgress: {percent:3.0f}%".format(percent=percent))


import json
from subprocess import check_output
from conduitcore.process.cli.CliCommand import CliCommand



def get_hashed_filelist(strip_path_part, directory):
    """
    e.g. get_hashed_filelist("/home/user/", "/home/user/test")
    :param strip_path_part: part of the path to be removed for the key
    :param directory: directory for which the hashed file list is to be created
    :return: hashed file list
    """
    cli = CliCommand.get("summainstdout", dict(package_dir=directory))
    summain_out = check_output(cli)
    json_summain_out = json.loads(summain_out)
    result = {}
    for entry in json_summain_out:
        if "SHA256" in entry:
            key = entry['Name'].lstrip(strip_path_part)
            result[key] = {"hash": entry['SHA256'], "path": entry["Name"]}
    return result




def get_package_from_directory_storage(task_context_path, package_uuid, package_extension, tl):
    from config.configuration import config_path_storage

    pts = DirectoryPairtreeStorage(config_path_storage)
    parent_object_path = pts.get_object_path(package_uuid)

    package_in_dip_work_dir = os.path.join(task_context_path, ("%s.%s" % (package_uuid, package_extension)))
    package_source_size = fsize(parent_object_path)
    tl.addinfo("Source: %s (%d)" % (parent_object_path, package_source_size))
    tl.addinfo("Target: %s" % package_in_dip_work_dir)
    total_bytes_read = 0
    with open(package_in_dip_work_dir, 'wb') as target_file:
        for chunk in FileBinaryDataChunks(parent_object_path, 65536).chunks(total_bytes_read):
            target_file.write(chunk)
        total_bytes_read += package_source_size
        target_file.close()
        check_transfer(parent_object_path, package_in_dip_work_dir, tl)


def make_storage_directory_path(identifier, version):
    """Used for remote (no access to storage backend)"""
    pts = DirectoryPairtreeStorage(config_path_storage)
    return os.path.join(pts.get_dir_path_from_id(identifier), "data", version, uri_to_safe_filename(identifier))


def make_storage_data_directory_path(identifier):
    """Used for remote (no access to storage backend)"""
    pts = DirectoryPairtreeStorage(config_path_storage)
    return os.path.join(pts.get_dir_path_from_id(identifier), "data")


def update_state(state_xml_file, identifier, version):
    ip_state = IpState.from_path(state_xml_file) if os.path.exists(state_xml_file) else IpState.from_parameters(0, False, last_task_value="stored")
    ip_state.set_version(version)
    ip_state.set_identifier(identifier)
    ip_state.write_doc(state_xml_file)


def files_identical(file1, file2):
    if not (os.path.exists(file1) and os.path.exists(file2)):
                return False
    checksum_source_file = ChecksumFile(file1).get('SHA-256')
    checksum_target_file = ChecksumFile(file2).get('SHA-256')
    logger.debug("f1: %s, f2: %s" % (file1, file2))
    logger.debug("cs1: %s, cs2: %s" % (checksum_source_file, checksum_target_file))
    return checksum_source_file == checksum_target_file


class DirectoryPairtreeStorage(object):
    """
    Pairtree storage class allowing to build a filesystem hierarchy to store objects that are located by mapping identifier strings to object directory (or folder) paths.
    """

    storage_factory = None
    repository_storage_dir = None

    def __init__(self, repository_storage_dir):
        """
        Constructor initialises pairtree repository

        @type       repository_storage_dir: string
        @param      repository_storage_dir: repository storage directory
        """
        self.storage_factory = PairtreeStorageFactory()
        self.repository_storage_dir = repository_storage_dir
        self.repo_storage_client = self.storage_factory.get_store(store_dir=self.repository_storage_dir, uri_base="http://")

    def store(self, identifier, source_directory, progress_reporter=default_reporter):
        """
        Storing a directory in the pairtree path according to the given identifier. If a version of the object exists,
        a new version is created.

        @type       identifier: string
        @param      identifier: Identifier
        @type:      source_directory: string
        @param:     source_directory: Source directory path with the content to be stored in the repository
        @type:      progress_reporter: function
        @param:     progress_reporter: progress reporter function
        @raise:     IOError: If the checksum of the copied file is incorrect
        """
        #object_path = self.get_object_path(identifier)
        dirpath = self.repo_storage_client._id_to_dirpath(identifier)
        r = self.repository_storage_dir
        next_version = self._next_version(identifier)
        target_data_directory = os.path.join(dirpath, "data")
        mkdir_p(target_data_directory)
        target_data_version_directory = os.path.join(target_data_directory, next_version)
        target_data_version_asset_directory = os.path.join(target_data_version_directory, uri_to_safe_filename(identifier))
        shutil.copytree(source_directory, target_data_version_asset_directory)
        progress_reporter(100)
        return next_version

    def get_dir_path_from_id(self, identifier):
        return self.repo_storage_client._id_to_dirpath(identifier)

    def identifier_object_exists(self, identifier):
        """
        Verify if an object of the given identifier exists in the repository

        @type       identifier: string
        @param      identifier: Identifier
        @rtype:     boolean
        @return:    True if the object exists, false otherwise
        """
        logger.debug("Looking for object at path: %s/data" % self.repo_storage_client._id_to_dirpath(identifier))
        return self.repo_storage_client.exists(identifier, "data")

    def identifier_version_object_exists(self, identifier, version_num):
        """
        Verify if the given version of the object exists in the repository

        @type       identifier: string
        @param      identifier: Identifier
        type        version_num: int
        @param      version_num: version number
        @rtype:     boolean
        @return:    True if the object exists, false otherwise
        """
        version = '%05d' % version_num
        return self.repo_storage_client.exists(identifier, "data/%s" % version)

    def _get_version_parts(self, identifier):
        """
        Get version directories

        @type       identifier: string
        @param      identifier: Identifier
        @rtype:     list
        @return:    List of directories of the versions
        """
        return self.repo_storage_client.list_parts(identifier, "data")

    def _next_version(self, identifier):
        """
        Get next formatted version directory name

        @type       identifier: string
        @param      identifier: Identifier
        @rtype:     string
        @return:    Formatted version string (constant VersionDirFormat)
        """
        if not self.identifier_object_exists(identifier):
            return VersionDirFormat % 1
        version_num = 1
        while self.identifier_version_object_exists(identifier, version_num):
            version_num += 1
        return VersionDirFormat % version_num

    def curr_version(self, identifier):
        """
        Get current formatted version directory name

        @type       identifier: string
        @param      identifier: Identifier
        @rtype:     string
        @return:    Formatted version string (constant VersionDirFormat)
        """
        return VersionDirFormat % self.curr_version_num(identifier)

    def curr_version_num(self, identifier):
        """
        Get current version number

        @type       identifier: string
        @param      identifier: Identifier
        @rtype:     int
        @return:    Current version number
        """
        if not self.identifier_object_exists(identifier):
            return 1
        version_num = 1
        while self.identifier_version_object_exists(identifier, version_num):
            version_num += 1
        version_num -= 1
        return version_num

    def get_object_path(self, identifier, version_num=0):
        """
        Get absolute file path of the stored object. If the version number is omitted, the path of the highest version
        number is returned.

        @type       identifier: string
        @param      identifier: Identifier
        @type       version_num: int
        @param      version_num: version number
        @rtype:     string
        @return:    Absolute file path of the stored object
        @raise      ObjectNotFoundException if the file is not available
        """
        if not self.identifier_object_exists(identifier):
            raise ValueError("No repository object for id '%s'. Unable to get requested version object path." % identifier)
        if version_num == 0:
            version_num = self.curr_version_num(identifier)
        if not self.identifier_version_object_exists(identifier, version_num):
            raise ValueError("Repository object '%s' has no version %d." % (identifier, version_num))
        version = '%05d' % version_num
        repo_obj = self.repo_storage_client.get_object(identifier, False)
        repo_obj_path = uri_to_safe_filename( os.path.join(repo_obj.id_to_dirpath(), "data/%s" % version))
        try:
            return next(os.path.join(repo_obj_path, f) for f in os.listdir(repo_obj_path) if os.path.isdir(os.path.join(repo_obj_path, f)))
        except StopIteration:
            raise ObjectNotFoundException("The file object does not exist in the repository")

    def get_object_item_stream(self, identifier, dataset_code, entry):
        """
        Get stream of tar file entry.

        @type       identifier: string
        @param      identifier: Identifier
        @type       entry: string
        @param      entry: tar file entry (path within tar file)
        @rtype:     binary
        @return:    File content
        @raise      KeyError if the tar entry does not exist in the stored package
        """
        object_path = self.get_object_path(identifier)
        version = self.curr_version(identifier)

        dataset_path = os.path.join(object_path, representations_directory, "%s.tar" % dataset_code)

        t = tarfile.open(dataset_path, 'r')
        logger.debug("Trying to access entry %s" % entry)
        try:
            info = t.getmember(entry)
            f = t.extractfile(info)
            inst = ChunkedTarEntryReader(t)
            return inst.chunks(entry)
        except KeyError:
            logger.error('ERROR: Did not find %s in tar archive' % entry)
            raise ObjectNotFoundException("Entry not found in repository object")

    def latest_version_ip_list(self) -> list:
        """
        Get a list of latest version packages from repository storage.
        @return:    List of dictionary items of IPs available in repository storage.
        """
        files = rec_find_files(self.repository_storage_dir)
        sortkeyfn = lambda s: s[1]
        tuples = []
        for repofile in files:
            if repofile.endswith(".tar"):
                f, fname = os.path.split(repofile)
                if f.startswith("pairtree_root"):
                    version = f[-5:] if f[-5:] != '' else '00001'
                    repoitem = (repofile, version)
                    tuples.append(repoitem)
        tuples.sort(key=sortkeyfn, reverse=True)
        items_grouped_by_version = []
        for key, valuesiter in groupby(tuples, key=sortkeyfn):
            items_grouped_by_version.append(dict(version=key, items=list(v[0] for v in valuesiter)))
        lastversionfiles = []
        for version_items in items_grouped_by_version:
            for item in version_items['items']:
                p, f = os.path.split(item)
                p2 = os.path.join(self.repository_storage_dir, p[:p.find("/data/")])
                obj_id = self.repo_storage_client._get_id_from_dirpath(p2)
                if not obj_id in [x['id'] for x in lastversionfiles]:
                    lastversionfiles.append({ "id": obj_id, "version": version_items['version'], "path": item})
        return lastversionfiles

    def trigger_new_version(self, uuid, identifier):
        """
        Trigger new version depending on changed files in working directory compared to the data set in storage.
        :param uuid: UUID of working directory
        :param identifier: Data asset identifier
        :return: True, if new version is triggered, False otherwise
        """
        working_dir = os.path.join(config_path_work, uuid)
        # dpts = DirectoryPairtreeStorage(config_path_storage)
        if self.identifier_object_exists(identifier):
            version = self.curr_version(identifier)
            data_asset_last_version_path = os.path.join(make_storage_data_directory_path(identifier), version, uri_to_safe_filename(identifier))
            working_distributions_dir = os.path.join(working_dir, representations_directory)
            if not os.path.exists(working_distributions_dir):
                logger.debug("New version is not triggered because working catalogue directory does not exist.")
                return False
            stored_distributions_dir = os.path.join(data_asset_last_version_path, representations_directory)
            dataset_dirs = get_immediate_subdirectories(working_distributions_dir)
            for dataset_dir in dataset_dirs:
                dataset_package_file = os.path.join(working_distributions_dir, "%s.tar" % dataset_dir)
                dataset_package_stored_file = os.path.join(stored_distributions_dir, "%s.tar" % dataset_dir)
                files_ident = files_identical(dataset_package_file, dataset_package_stored_file)
                if not files_ident:
                    logger.debug("New version triggered because hash of dataset packages is not identical")
                    return True
        logger.debug("New version not triggered.")
        return False

    def store_working_directory(self, uuid, identifier):
        """
        Store working directory
        :param uuid: UUID of working directory
        :param identifier: Data asset identifier
        :return: version
        """
        working_dir = os.path.join(config_path_work, uuid)
        # dpts = DirectoryPairtreeStorage(config_path_storage)
        version = self._next_version(identifier) if self.trigger_new_version(uuid, identifier) else self.curr_version(identifier)
        target_dir = os.path.join(make_storage_data_directory_path(identifier), version, uri_to_safe_filename(identifier))
        changed = False
        for path, dirs, files in os.walk(os.path.abspath(working_dir)):
            sub_path = path.replace(working_dir, "").lstrip("/")
            for file in files:
                # copy only packaged datasets, not the directories
                if not path.startswith(os.path.join(working_dir, representations_directory)) or fnmatch.fnmatch(file, "*.tar"):
                    source = os.path.join(working_dir, sub_path, file)
                    target = os.path.join(target_dir, sub_path, file)
                    # copy files only if they are not identical
                    if not files_identical(source, target):
                        copy_file_with_base_directory(working_dir, target_dir, sub_path, file)
                        changed = True
        # update state in storage and working directory if any files have been changed
        if changed:
            storage_state_file = os.path.join(target_dir, "state.xml")
            working_state_file = os.path.join(working_dir, "state.xml")
            update_state(working_state_file, identifier, version)
            shutil.copy2(working_state_file, storage_state_file)
        return version



class TestDirectoryPairtreeStorage(unittest.TestCase):
    source_dir = root_dir + '/testresources/dma-test-asset/foo'
    test_repo_resources = root_dir + '/testresources/test-repo-dirassets/'
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
        logger.debug(content)

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
