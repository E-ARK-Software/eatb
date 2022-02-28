#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import pathlib
import re
import sys

from pairtree import PairtreeStorageFactory, ObjectNotFoundException, shutil
from eatb.utils.reporters import default_reporter

from eatb.storage.checksum import check_transfer
from eatb.utils.fileutils import fsize, to_safe_filename, rec_find_files, FileBinaryDataChunks
from eatb.packaging.tar_entry_reader import ChunkedTarEntryReader

logger = logging.getLogger(__name__)


import os.path
import tarfile
from itertools import groupby

VersionDirFormat = 'v%05d'


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


class PairtreeStorage():
    """
    Pairtree storage class allowing to build a filesystem hierarchy for holding objects that are located by mapping
    identifier strings to object directory (or folder) paths with two characters at a time.
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

    # noinspection PyProtectedMember
    def store(self, identifier, source_directory, copy_dir=False, progress_reporter=default_reporter):
        """
        Storing a directory in the pairtree path according to the given identifier. If a version of the object exists,
        a new version is created.
        :param identifier: identifier
        :param source_directory: source directory
        :param progress_reporter: progress reporter
        :return:
        """
        dirpath = self.repo_storage_client._id_to_dirpath(identifier)
        next_version = self._next_version(identifier)
        target_data_directory = os.path.join(dirpath, "data")
        pathlib.Path(target_data_directory).mkdir(parents=True, exist_ok=True)
        target_data_version_directory = os.path.join(target_data_directory, next_version)
        bag_name = self.get_bag_name(identifier, next_version, 1)
        target_data_version_asset_directory = os.path.join(target_data_version_directory, "content", bag_name)
        if copy_dir:
            shutil.copytree(source_directory, target_data_version_asset_directory)
        else:
            os.makedirs(target_data_version_asset_directory, exist_ok=True)
            archive_file = "%s.tar" % to_safe_filename(identifier)
            src_file_path = os.path.join(source_directory, archive_file)
            target_file_path = os.path.join(target_data_version_asset_directory, archive_file)
            if not os.path.exists(src_file_path):
                raise ValueError("Archive file does not exist: %s" % src_file_path)
            shutil.copy2(src_file_path, target_file_path)
        progress_reporter(100)
        return next_version

    def get_bag_name(self, identifier: str, version: str, bagnr: int):
        safe_identifier_name = to_safe_filename(identifier)
        bag_dir_name = "b%05d" % int(bagnr)
        bag_name = "%s_%s_%s" % (safe_identifier_name, version, bag_dir_name)
        return bag_name

    def identifier_object_exists(self, identifier):
        """
        Verify if an object of the given identifier exists in the repository

        @type       identifier: string
        @param      identifier: Identifier
        @rtype:     boolean
        @return:    True if the object exists, false otherwise
        """
        logger.debug("Looking for object at path: %s/data" % self.repo_storage_client._id_to_dirpath(identifier))
        return self.repo_storage_client.exists(identifier, os.path.join("data", "v%05d" % 0))

    def identifier_version_object_exists(self, identifier, version_num):
        """
        Verify if the given version of the object exists in the repository
        :param identifier: identifier
        :param version_num: version number
        :return:
        """
        version = 'v%05d' % version_num
        return self.repo_storage_client.exists(identifier, "data/%s" % version)

    def _get_version_parts(self, identifier):
        """
        Get version directories
        :param identifier: identifier
        :return: version parts
        """
        return self.repo_storage_client.list_parts(identifier, "data")

    def _next_version(self, identifier):
        """
        Get next formatted version directory name
        :param identifier: identifier
        :return: next formatted version directory name
        """
        if not self.identifier_object_exists(identifier):
            return VersionDirFormat % 0
        version_num = 1
        while self.identifier_version_object_exists(identifier, version_num):
            version_num += 1
        return VersionDirFormat % version_num

    def curr_version(self, identifier):
        """
        Get current formatted version directory name
        :param identifier: identifier
        :return: current formatted version directory name
        """
        curr_version_num = self.curr_version_num(identifier)
        return VersionDirFormat % curr_version_num

    def curr_version_num(self, identifier):
        """
        Get current version number
        :param identifier: identifier
        :return: current version number
        """
        if not self.identifier_object_exists(identifier):
            return -1
        version_num = 0
        while self.identifier_version_object_exists(identifier, version_num):
            version_num += 1
        version_num -= 1
        return version_num

    def get_object_path(self, identifier, version_num=0):
        """
        Get absolute file path of the stored object. If the version number is omitted, the path of the highest version
        number is returned.
        :param identifier: identifier
        :param version_num: version number
        :return: absolute file path of the stored object
        """
        if not self.identifier_object_exists(identifier):
            raise ObjectNotFoundException("No repository object for id '%s'. "
                             "Unable to get requested version object path." % identifier)
        if version_num == 0:
            version_num = self.curr_version_num(identifier)
        if not self.identifier_version_object_exists(identifier, version_num):
            raise ValueError("Repository object '%s' has no version %d." % (identifier, version_num))
        version = 'v%05d' % version_num
        repo_obj = self.repo_storage_client.get_object(identifier, False)
        repo_obj_path = to_safe_filename(os.path.join(repo_obj.id_to_dirpath(), "data/%s" % version))
        try:
            return next(os.path.join(repo_obj_path, f) for f in os.listdir(repo_obj_path)
                        if os.path.isdir(os.path.join(repo_obj_path, f)))
        except StopIteration:
            raise ObjectNotFoundException("The file object does not exist in the repository")

    def get_chunked_tar_entry_reader(self, identifier: str) -> ChunkedTarEntryReader:
        tar_file_path = os.path.join(self.get_object_path(identifier), "%s.tar" % to_safe_filename(identifier))
        tar_file = tarfile.open(tar_file_path, 'r')
        return ChunkedTarEntryReader(tar_file)

    # noinspection PyProtectedMember
    def latest_version_ip_list(self) -> list:
        """
        Get a list of latest version packages from repository storage.
        :return: list of latest version packages
        """
        files = rec_find_files(self.repository_storage_dir)
        sortkeyfn = lambda s: s[1]
        tuples = []
        for repofile in files:
            if repofile.endswith(".tar"):
                f, _ = os.path.split(repofile)
                version = re.search(r'v[0-9]{5,5}', f).group(0)
                repoitem = (repofile, int(re.search(r'\d+', version).group(0)))
                tuples.append(repoitem)
        tuples.sort(key=sortkeyfn, reverse=True)
        items_grouped_by_version = []
        for key, valuesiter in groupby(tuples, key=sortkeyfn):
            items_grouped_by_version.append(dict(version=key, items=list(v[0] for v in valuesiter)))
        lastversionfiles = []
        for version_items in items_grouped_by_version:
            for item in version_items['items']:
                p, f = os.path.split(item)
                p2 = os.path.join(self.repository_storage_dir, p[:p.find("/data/v")])
                obj_id = self.repo_storage_client._get_id_from_dirpath(p2)
                if obj_id not in [x['id'] for x in lastversionfiles]:
                    lastversionfiles.append({"id": obj_id, "version": version_items['version'], "path": item})
        return lastversionfiles
