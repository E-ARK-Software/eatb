import os
import pathlib
import re
import shutil
import tarfile
import fnmatch

from itertools import groupby
from eatb import VersionDirFormat
from eatb.checksum import check_transfer
from eatb.ipstate import IpState
from eatb.utils.fileutils import rec_find_files, fsize, FileBinaryDataChunks
from eatb.utils.fileutils import to_safe_filename, list_files_in_dir, copy_file_with_base_directory
from pairtree import PairtreeStorageFactory, ObjectNotFoundException
from eatb import logger
from eatb.checksum import files_identical
from eatb.packaging import ChunkedTarEntryReader
from eatb.utils.reporters import default_reporter


class PairtreeStorage:
    """
    Pairtree storage class allowing to build a filesystem hierarchy for holding objects that are located by mapping
    identifier strings to object directory (or folder) paths with two characters at a time.
    """
    storage_factory = None
    repository_storage_dir = None

    def __init__(self, repository_storage_dir, representations_directory="representations"):
        """
        Constructor initialises pairtree repository
        :param repository_storage_dir: repository storage directory
        :param representations_directory: representations directory
        """
        #super().__init__(repository_storage_dir)
        self.storage_factory = PairtreeStorageFactory()
        self.repository_storage_dir = repository_storage_dir
        self.representations_directory = representations_directory
        self.repo_storage_client = self.storage_factory.get_store(store_dir=repository_storage_dir, uri_base="http://")
        self.representations_directory = representations_directory

    # noinspection PyProtectedMember
    def store(self, identifier, source_file_path, progress_reporter=default_reporter):
        """
        Storing a directory in the pairtree path according to the given identifier. If a version of the object exists,
        a new version is created.
        :param identifier: identifier
        :param source_file_path: source file path
        :param progress_reporter: progress reporter
        :return:
        """
        # pairtree object path
        pairtree_object_path = self.repo_storage_client._id_to_dirpath(identifier)
        # next version string
        next_version = self._next_version(identifier)
        # data directory
        target_data_directory = os.path.join(pairtree_object_path, "data")
        # create data directory path
        pathlib.Path(target_data_directory).mkdir(parents=True, exist_ok=True)
        # data version directory
        target_data_version_directory = os.path.join(target_data_directory, next_version)
        # create data version directory
        os.makedirs(target_data_version_directory, exist_ok=True)

        # archive file name
        safe_identifier_name = to_safe_filename(identifier)
        archive_file = "%s.tar" % safe_identifier_name
        # check source file exists
        if not os.path.exists(source_file_path):
            raise ValueError("Source file does not exist: %s" % source_file_path)
        # target file path
        target_file_path = os.path.join(target_data_version_directory, archive_file)
        # copy file
        shutil.copy2(source_file_path, target_file_path)
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
        logger.debug("Looking for object at path: %s/data" % (self.repo_storage_client._id_to_dirpath(identifier)))
        return self.repo_storage_client.exists(identifier, os.path.join("data"))

    def identifier_version_object_exists(self, identifier, version_num):
        """
        Verify if the given version of the object exists in the repository
        :param identifier: identifier
        :param version_num: version number
        :return:
        """
        version = VersionDirFormat % version_num
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

    def get_object_path(self, identifier):
        """
        Get absolute file path of the stored object. If the version number is omitted, the path of the highest version
        number is returned.
        :param identifier: identifier
        :param version_num: version number
        :return: absolute file path of the stored object
        """
        curr_version = self.curr_version(identifier)
        dirpath = self.repo_storage_client._id_to_dirpath(identifier)
        target_data_directory = os.path.join(dirpath, "data")
        target_data_version_directory = os.path.join(target_data_directory, curr_version)
        path_to_object = os.path.join(target_data_version_directory, "%s.tar" % to_safe_filename(identifier))
        if os.path.exists(path_to_object):
            logger.debug("Package file found at: %s" % path_to_object)
            return path_to_object
        raise ObjectNotFoundException("Package file not found")

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


    # noinspection PyProtectedMember
    def get_dir_path_from_id(self, identifier):
        """
        Get directory path from id
        :param identifier: identifier
        :return: directory path
        """
        return self.repo_storage_client._id_to_dirpath(identifier)

    def get_tar_file_path(self, identifier):
        curr_version = self.curr_version(identifier)
        dirpath = self.repo_storage_client._id_to_dirpath(identifier)
        target_data_directory = os.path.join(dirpath, "data")
        target_data_version_directory = os.path.join(target_data_directory, curr_version)
        bag_name = self.get_bag_name(identifier, curr_version, 1)
        target_data_version_asset_directory = os.path.join(target_data_version_directory, "content")
        tar_file_path = os.path.join(target_data_version_asset_directory, "%s.tar" % bag_name)
        if os.path.exists(tar_file_path):
            logger.debug("Package file found at: %s" % tar_file_path)
            return tar_file_path
        raise ObjectNotFoundException("Package file not found")

    def get_object_item_stream(self, identifier, entry, tar_file=None):
        """
        Get stream of a representation tar file entry
        :param identifier: package identifier
        :param entry: entry of the tar file
        :tar_file: path to tar file (optional)
        :return: chunks iterator of the tar file
        """
        tar_file_path = self.get_object_path(identifier)
        if os.path.exists(tar_file_path):
            logger.debug("tar file found at: %s" % entry)
        t = tar_file if tar_file else tarfile.open(tar_file_path, 'r')
        logger.debug("Accessing access entry %s" % entry)
        try:
            inst = ChunkedTarEntryReader(t)
            return inst.chunks(entry)
        except KeyError:
            logger.error('ERROR: Did not find %s in tar archive' % entry)
            raise ObjectNotFoundException("Entry not found in repository object")

    def trigger_new_version(self, uuid, identifier, config_path_work, storage_directory):
        """
        Trigger new version depending on changed files in working directory compared to the data set in storage.
        :param storage_directory:
        :param config_path_work:
        :param uuid: UUID of working directory
        :param identifier: Data asset identifier
        :return: True, if new version is triggered, False otherwise
        """
        working_dir = os.path.join(config_path_work, uuid)
        if self.identifier_object_exists(identifier):
            version = self.curr_version(identifier)
            data_asset_last_version_path = os.path.join(
                make_storage_data_directory_path(identifier, storage_directory),
                version, to_safe_filename(identifier))
            working_distributions_dir = os.path.join(working_dir, self.representations_directory)
            if not os.path.exists(working_distributions_dir):
                logger.debug("New version is not triggered because working catalogue directory does not exist.")
                return False
            stored_distributions_dir = os.path.join(data_asset_last_version_path, self.representations_directory)
            distribution_files = list_files_in_dir(working_distributions_dir)
            for dataset_dir in distribution_files:
                dataset_package_file = os.path.join(working_distributions_dir, "%s.tar" % dataset_dir)
                dataset_package_stored_file = os.path.join(stored_distributions_dir, "%s.tar" % dataset_dir)
                files_ident = files_identical(dataset_package_file, dataset_package_stored_file)
                if not files_ident:
                    logger.debug("New version triggered because hash of dataset packages is not identical")
                    return True
        logger.debug("New version not triggered.")
        return False


def update_state(state_xml_file, identifier, version):
    ip_state = IpState.from_path(state_xml_file) if os.path.exists(state_xml_file) \
        else IpState.from_parameters(0, False, last_task_value="stored")
    ip_state.set_version(version)
    ip_state.set_identifier(identifier)
    ip_state.write_doc(state_xml_file)


def get_package_from_directory_storage(task_context_path, package_uuid, package_extension,
                                       tl, config_path_storage):
    pts = PairtreeStorage(config_path_storage)
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


def make_storage_directory_path(identifier, version, config_path_storage):
    """Used for remote (no access to storage backend)"""
    pts = PairtreeStorage(config_path_storage)
    return os.path.join(pts.get_dir_path_from_id(identifier), "data", version, to_safe_filename(identifier))


def make_storage_data_directory_path(identifier, config_path_storage):
    """Used for remote (no access to storage backend)"""
    pts = PairtreeStorage(config_path_storage)
    return os.path.join(pts.get_dir_path_from_id(identifier), "data")


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