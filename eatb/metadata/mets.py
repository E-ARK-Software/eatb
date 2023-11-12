#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fnmatch
import os

import eatb.metadata

from eatb.metadata.parsed_mets import ParsedMets
from eatb.metadata.mets_validation import XLINK_NS, METS_NS
from eatb.utils.fileutils import rec_find_files


folders_with_USE = ['documentation', 'schemas', 'representations', "data"]

logger = eatb.metadata.logger


def get_package_mets_files_from_basedir(base_directory):
        """
        Get list of information package METS file paths based on a directory which contains information packages in subdirectories.

        @type       base_directory: str
        @param      base_directory: Directory which contains information packages in subdirectories.
        @rtype:     list
        @return:    String list of information package METS file paths
        """
        return list(rec_find_files(base_directory, include_files_rgxs=[r'.*METS.xml$'],
                                    exclude_dirsfiles_rgxs=None))


def get_mets_obj_id(mets_file_path):
        """
        Get identifier from mets file

        @type       mets_file_path: str
        @param      mets_file_path: METS file path
        @rtype:     str
        @return:    Object identifier
        """
        package_path, file_name = os.path.split(mets_file_path)
        pm = ParsedMets(package_path)
        pm.load_mets(mets_file_path)
        return str(pm.get_obj_id())


def get_mets_objids_from_basedir(base_directory):
        """
        Get list of OBJID strings from METS files based on a directory which contains information packages in subdirectories.

        @type       base_directory: str
        @param      base_directory: Directory which contains information packages in subdirectories.
        @rtype:     list
        @return:    Object identifier
        """
        mets_file_paths = get_package_mets_files_from_basedir(base_directory)
        mets_obj_ids = []
        for mets_file_path in mets_file_paths:
            mets_obj_ids.append(get_mets_obj_id(mets_file_path))
        return mets_obj_ids


def get_folder_with_USE(path):
    try:
        dirs = path.split('/')
        for dir in dirs[::-1]:
            if dir in folders_with_USE:
                return dir
    except Exception as e:
        logger.debug('Parent directory not used')
        logger.debug(e)
    return 'other'


