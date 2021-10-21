#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tarfile
from pathlib import Path

from eatb.storage.checksum import ChecksumFile, ChecksumAlgorithm


def create_package(input_directory, packagename, gunzip=False, output_directory=None, use_input_dir_as_root=False, exclude=[]) -> str:
    """
    Create package
    :param input_directory: Input directory
    :param packagename: Name of the package file
    :param output_directory: Output directory (same as input directory if not provided)
    :gunzip create compressed container package
    :return: md5checksum of package
    """

    # append generation number to tar file; if tar file exists, the generation number is incremented
    input_path = Path(input_directory)
    extension = '.tar.gz' if gunzip else '.tar'
    if not output_directory:
        output_directory = input_path.parent
    storage_tar_file = os.path.join(output_directory, packagename + extension)
    write_mode = "w:gz" if gunzip else "w:"
    tar = tarfile.open(storage_tar_file, "w:")
    total = sum([len(files) for (root, dirs, files) in os.walk(input_directory)])
    i = 0
    for subdir, dirs, files in os.walk(input_directory):

        for dir in dirs:
            entry = os.path.join(os.path.basename(input_directory), subdir, dir)
            base = os.path.basename(input_directory) if use_input_dir_as_root else ""
            if not os.listdir(entry):
                tar.add(entry, arcname=os.path.join(base, os.path.relpath(entry, input_directory)))

        for file in files:
            entry = os.path.join(os.path.basename(input_directory), subdir, file)
            base = os.path.basename(input_directory) if use_input_dir_as_root else ""

            def exclude_func(file_name):
                return os.path.basename(file_name) in exclude

            tar.add(entry, arcname=os.path.join(base, os.path.relpath(entry, input_directory)))
            if i % 10 == 0:
                perc = (i * 100) / total
            i += 1
    tar.close()

    checksum_file = ChecksumFile(storage_tar_file)
    return checksum_file.get(ChecksumAlgorithm.MD5)
