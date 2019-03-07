#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import tarfile
from pathlib import Path

from earchivingtoolbox.storage.checksum import ChecksumFile, ChecksumAlgorithm

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402


def create_package(input_directory, packagename) -> str:
    """
    Create package
    :param input_directory: Input directory
    :return: md5checksum of package
    """

    # append generation number to tar file; if tar file exists, the generation number is incremented
    input_path = Path(input_directory)
    storage_tar_file = os.path.join(input_path.parent, packagename + '.tar')
    tar = tarfile.open(storage_tar_file, "w:")
    total = sum([len(files) for (root, dirs, files) in os.walk(input_directory)])
    i = 0
    for subdir, dirs, files in os.walk(input_directory):

        for dir in dirs:
            entry = os.path.join(subdir, dir)
            if not os.listdir(entry):
                tar.add(entry, arcname=os.path.relpath(entry, input_directory))

        for file in files:
            entry = os.path.join(subdir, file)
            tar.add(entry, arcname=os.path.relpath(entry, input_directory))
            if i % 10 == 0:
                perc = (i * 100) / total
            i += 1
    tar.close()

    checksum_file = ChecksumFile(storage_tar_file)
    return checksum_file.get(ChecksumAlgorithm.MD5)
