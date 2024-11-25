import os
import pathlib
import re
import shutil
from itertools import groupby
from pairtree import PairtreeStorageFactory, ObjectNotFoundException
from eatb import VersionDirFormat
from eatb.ipstate import IpState
from eatb.utils.fileutils import rec_find_files
from eatb.utils.fileutils import to_safe_filename
from eatb import logger
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

    def identifier_object_exists(self, identifier):
        """
        Verify if an object of the given identifier exists in the repository

        @type       identifier: string
        @param      identifier: Identifier
        @rtype:     boolean
        @return:    True if the object exists, false otherwise
        """
        logger.debug(f"Looking for object at path: {self.repo_storage_client._id_to_dirpath(identifier)}/data")
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
            return VersionDirFormat % 1
        version_num = 2
        while self.identifier_version_object_exists(identifier, version_num):
            version_num += 1
        return VersionDirFormat % version_num
    
    def next_version(self, identifier):
        """
        Get next formatted version directory name
        :param identifier: identifier
        :return: next formatted version directory name
        """
        return self._next_version(identifier)

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
        version_num = 1
        while self.identifier_version_object_exists(identifier, version_num):
            version_num += 1
        version_num -= 1
        return version_num

    def get_object_path(self, identifier):
        """
        Get the absolute path of the stored object directory. Verifies that the directory is not empty.
        :param identifier: identifier
        :return: absolute path to the stored object directory
        """
        curr_version = self.curr_version(identifier)
        dirpath = self.repo_storage_client._id_to_dirpath(identifier)
        target_data_directory = os.path.join(dirpath, "data")
        target_data_version_directory = os.path.join(target_data_directory, curr_version)

        if not os.path.exists(target_data_version_directory):
            raise ObjectNotFoundException(f"Version directory not found: {target_data_version_directory}")
        
        # Check if the directory is empty
        if not os.listdir(target_data_version_directory):  # os.listdir returns an empty list if the directory is empty
            raise ObjectNotFoundException(f"Directory is empty: {target_data_version_directory}")

        logger.debug("Valid data directory found at: %s", target_data_version_directory)
        return target_data_version_directory

    # noinspection PyProtectedMember
    def latest_version_ip_list(self) -> list:
        """
        Get a list of the latest version directories from repository storage.
        :return: list of latest version directories
        """
        # Find all directories recursively in the repository storage
        directories = rec_find_files(self.repository_storage_dir)
        sortkeyfn = lambda s: s[1]  # Sort by version number
        tuples = []

        for directory in directories:
            if "/data/v" in directory:
                # Extract version from the path
                version_match = re.search(r'v[0-9]{5,5}', directory)
                if version_match:
                    version = version_match.group(0)
                    repoitem = (directory, int(re.search(r'\d+', version).group(0)))
                    tuples.append(repoitem)

        # Sort by version number (descending order)
        tuples.sort(key=sortkeyfn, reverse=True)

        # Group by version
        items_grouped_by_version = []
        for key, valuesiter in groupby(tuples, key=sortkeyfn):
            items_grouped_by_version.append(dict(version=key, items=list(v[0] for v in valuesiter)))

        lastversionfiles = []
        for version_items in items_grouped_by_version:
            for item in version_items['items']:
                # Get the root directory for the object
                p, _ = os.path.split(item)
                root_dir = os.path.join(self.repository_storage_dir, p[:p.find("/data/v")])
                obj_id = self.repo_storage_client._get_id_from_dirpath(root_dir)

                # Avoid duplicates based on object ID
                if obj_id not in [x['id'] for x in lastversionfiles]:
                    lastversionfiles.append({
                        "id": obj_id,
                        "version": version_items['version'],
                        "path": item
                    })

        return lastversionfiles

    # noinspection PyProtectedMember
    def get_dir_path_from_id(self, identifier):
        """
        Get directory path from id
        :param identifier: identifier
        :return: directory path
        """
        return self.repo_storage_client._id_to_dirpath(identifier)


def update_state(state_xml_file, identifier, version):
    ip_state = IpState.from_path(state_xml_file) if os.path.exists(state_xml_file) \
        else IpState.from_parameters(0, False, last_task_value="stored")
    ip_state.set_version(version)
    ip_state.set_identifier(identifier)
    ip_state.write_doc(state_xml_file)


def make_storage_directory_path(identifier, version, config_path_storage):
    """Used for remote (no access to storage backend)"""
    pts = PairtreeStorage(config_path_storage)
    return os.path.join(pts.get_dir_path_from_id(identifier), "data", version, to_safe_filename(identifier))


def make_storage_data_directory_path(identifier, config_path_storage):
    """Used for remote (no access to storage backend)"""
    pts = PairtreeStorage(config_path_storage)
    return os.path.join(pts.get_dir_path_from_id(identifier), "data")
