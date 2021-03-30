#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fnmatch
import json
import logging
import os
import os.path
import shutil
from subprocess import check_output
import tarfile

from pairtree import PairtreeStorageFactory, ObjectNotFoundException

from eatb.packaging.tar_entry_reader import ChunkedTarEntryReader
from eatb.storage.checksum import check_transfer, ChecksumFile
from eatb.utils.fileutils import fsize, FileBinaryDataChunks, to_safe_filename, \
    copy_file_with_base_directory, list_files_in_dir

from eatb.cli.cli import CliCommands
from eatb.cli.cli import CliCommand
from eatb.storage.ipstate import IpState
from eatb.storage.pairtreestorage import PairtreeStorage

logger = logging.getLogger(__name__)

VersionDirFormat = '%05d'


def default_reporter(percent):
    print("\rProgress: {percent:3.0f}%".format(percent=percent))


def get_hashed_filelist(strip_path_part, directory, commands=CliCommands()):
    """
    e.g. get_hashed_filelist("/home/user/", "/home/user/test")
    :param commands:
    :param strip_path_part: part of the path to be removed for the key
    :param directory: directory for which the hashed file list is to be created
    :return: hashed file list
    """
    cli_command = CliCommand("summainstdout", commands.get_command_template("summainstdout"))
    command = cli_command.get_command(dict(package_dir=directory))
    summain_out = check_output(command)
    json_summain_out = json.loads(summain_out)
    result = {}
    for entry in json_summain_out:
        if "SHA256" in entry:
            key = entry['Name'].lstrip(strip_path_part)
            result[key] = {"hash": entry['SHA256'], "path": entry["Name"]}
    return result


def get_package_from_directory_storage(task_context_path, package_uuid, package_extension,
                                       tl, config_path_storage):
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
        check_transfer(parent_object_path, package_in_dip_work_dir)


def make_storage_directory_path(identifier, version, config_path_storage):
    """Used for remote (no access to storage backend)"""
    pts = DirectoryPairtreeStorage(config_path_storage)
    return os.path.join(pts.get_dir_path_from_id(identifier), "data", version, to_safe_filename(identifier))


def make_storage_data_directory_path(identifier, config_path_storage):
    """Used for remote (no access to storage backend)"""
    pts = DirectoryPairtreeStorage(config_path_storage)
    return os.path.join(pts.get_dir_path_from_id(identifier), "data")


def files_identical(file1, file2):
    if not (os.path.exists(file1) and os.path.exists(file2)):
        return False
    checksum_source_file = ChecksumFile(file1).get('SHA-256')
    checksum_target_file = ChecksumFile(file2).get('SHA-256')
    logger.debug("f1: %s, f2: %s" % (file1, file2))
    logger.debug("cs1: %s, cs2: %s" % (checksum_source_file, checksum_target_file))
    return checksum_source_file == checksum_target_file


def update_state(state_xml_file, identifier, version):
    ip_state = IpState.from_path(state_xml_file) if os.path.exists(state_xml_file) \
        else IpState.from_parameters(0, False, last_task_value="stored")
    ip_state.set_version(version)
    ip_state.set_identifier(identifier)
    ip_state.write_doc(state_xml_file)


class DirectoryPairtreeStorage(PairtreeStorage):
    """
    Pairtree storage class allowing to build a filesystem hierarchy to store objects that are located by mapping
    identifier strings to object directory (or folder) paths.
    """
    storage_factory = None
    repository_storage_dir = None

    def __init__(self, repository_storage_dir, representations_directory="representations"):
        """
        Constructor initialises pairtree repository
        :param repository_storage_dir: repository storage directory
        :param representations_directory: representations directory
        """
        super().__init__(repository_storage_dir)
        self.storage_factory = PairtreeStorageFactory()
        self.repository_storage_dir = repository_storage_dir
        self.representations_directory = representations_directory
        self.repo_storage_client = self.storage_factory.get_store(store_dir=repository_storage_dir, uri_base="http://")
        self.representations_directory = representations_directory

    # noinspection PyProtectedMember
    def get_dir_path_from_id(self, identifier):
        """
        Get directory path from id
        :param identifier: identifier
        :return: directory path
        """
        return self.repo_storage_client._id_to_dirpath(identifier)

    def get_tar_file_path(self, identifier, representation_label=None):
        object_path = self.get_object_path(identifier)
        if representation_label:
            tar_file_path = os.path.join(object_path, self.representations_directory, "%s.tar" % representation_label)
        else:
            tar_file_path = os.path.join(object_path, "%s.tar" % to_safe_filename(identifier))
        if os.path.exists(tar_file_path):
            logger.debug("Package file found at: %s" % tar_file_path)
            return tar_file_path
        raise ObjectNotFoundException("Package file not found")

    def get_object_item_stream(self, identifier, representation_label, entry, tar_file=None):
        """
        Get stream of a representation tar file entry
        :param identifier: package identifier
        :param representation_label: label of the representation (used in directory and file names), can be empty,
        tar assumed to be single package in that case
        :param entry: entry of the tar file
        :return: chunks iterator of the tar file
        """
        object_path = self.get_object_path(identifier)
        tar_file_name = "%s.tar" % representation_label if representation_label else to_safe_filename(identifier)
        tar_file_path = os.path.join(object_path, self.representations_directory, tar_file_name)
        if os.path.exists(tar_file_path):
            logger.debug("Packaged representation file found at: %s" % entry)
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

    def store(self, identifier, source_directory, progress_reporter=default_reporter, single_package=True):
        sdir = source_directory[:-1] if source_directory.endswith('/') else source_directory
        uuid = sdir[sdir.rfind('/')+1:]
        working_dir = sdir[:sdir.rfind('/')]
        return self.store_working_directory(uuid, identifier, working_dir, single_package=single_package)

    def store_working_directory(self, uuid, identifier, working_directory, single_package=True):
        """
        Store working directory either as single package or as representation packages
        :param uuid: UUID of working directory
        :param identifier: Object identifier
        :param working_directory: working directory
        :param single_package: store as single package or as representation packages
        :return: version of the stored object
        """
        if single_package:
            version = super().store(identifier, working_directory, copy_dir=True)
        else:
            version = self.store_working_directory_as_representation_packages(uuid, identifier, working_directory)
        return version

    def store_working_directory_as_representation_packages(self, uuid, identifier, working_directory):
        """
        Store working directory
        :param storage_directory:
        :param working_directory: working directory
        :param uuid: UUID of working directory
        :param identifier: Object identifier
        :return: version
        """
        working_dir = os.path.join(working_directory, uuid)
        version = self._next_version(identifier) \
            if self.trigger_new_version(uuid, identifier, working_directory, self.repository_storage_dir) \
            else self.curr_version(identifier)
        target_dir = os.path.join(make_storage_data_directory_path(identifier, self.repository_storage_dir), version,
                                  to_safe_filename(identifier))
        changed = False
        for path, _, files in os.walk(os.path.abspath(working_dir)):
            sub_path = path.replace(working_dir, "").lstrip("/")
            for file in files:
                # copy only packaged datasets, not the directories
                if not path.startswith(os.path.join(working_dir, self.representations_directory)) \
                        or fnmatch.fnmatch(file, "*.tar"):
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
