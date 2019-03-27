#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402

import logging

from pairtree import PairtreeStorageFactory, ObjectNotFoundException
from eatb.utils.reporters import default_reporter

from eatb.storage.checksum import ChecksumFile, ChecksumAlgorithm, check_transfer
from eatb.utils.fileutils import fsize, uri_to_safe_filename, rec_find_files, FileBinaryDataChunks
from eatb.packaging.tar_entry_reader import ChunkedTarEntryReader

logger = logging.getLogger(__name__)


import os
import os.path
import ntpath
import tarfile
from itertools import groupby

VersionDirFormat = '%05d'


def get_package_from_storage(storage, task_context_path, package_uuid, package_extension, tl):

    pts = PairtreeStorage(storage)
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
        check_transfer(parent_object_path, package_in_dip_work_dir)


class PairtreeStorage(object):
    """
    Pairtree storage class allowing to build a filesystem hierarchy for holding objects that are located by mapping identifier strings to object directory (or folder) paths with
    two characters at a time.
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

    def store(self, identifier, source_file, progress_reporter=default_reporter):
        """
        Storing an object in the pairtree path according to the given identifier. If a version of the object exists,
        a new version is created.

        @type       identifier: string
        @param      identifier: Identifier
        @type:      source_file: string
        @param:     source_file: Source file path to be stored in the repository
        @type:      progress_reporter: function
        @param:     progress_reporter: progress reporter function
        @raise:     IOError: If the checksum of the copied file is incorrect
        """
        repo_object = self.repo_storage_client.get_object(identifier, True)
        basename = ntpath.basename(source_file)
        next_version = self._next_version(identifier)
        with open(source_file, 'rb') as stream:
            repo_object.add_bytestream(basename, stream, path="data/%s" % next_version)
        progress_reporter(50)
        checksum_source_file = ChecksumFile(source_file).get(ChecksumAlgorithm.SHA256)
        checksum_target_file = ChecksumFile(self.get_object_path(identifier)).get(ChecksumAlgorithm.SHA256)
        if checksum_source_file != checksum_target_file:
            raise IOError("Storage of repository object for identifier '%s' failed!" % identifier)
        progress_reporter(100)

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
            raise ValueError("No repository object for id '%s'. Unable to get current version number." % identifier)
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
            return next(os.path.join(repo_obj_path, f) for f in os.listdir(repo_obj_path) if os.path.isfile(os.path.join(repo_obj_path, f)))
        except StopIteration:
            raise ObjectNotFoundException("The file object does not exist in the repository")

    def get_chunked_tar_entry_reader(self, identifier: str) -> ChunkedTarEntryReader:
        tar_file_path = self.get_object_path(identifier)
        tar_file = tarfile.open(tar_file_path, 'r')
        return ChunkedTarEntryReader(tar_file)

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
