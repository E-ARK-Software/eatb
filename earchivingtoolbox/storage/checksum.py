#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402

from earchivingtoolbox.utils.fileutils import fsize

import hashlib


class ChecksumAlgorithm:
    """
    Checksum algorithm
    """
    MD5, SHA256, NONE = range(3)

    @staticmethod
    def get(alg):
        """
        Get algorithm by string
        :param alg: Algorithm string
        :return: Checksum algorithm
        """
        if alg.lower() == "md5":
            return ChecksumAlgorithm.MD5
        elif alg.lower() == "sha256" or alg.lower() == "sha-256":
            return ChecksumAlgorithm.SHA256
        else:
            return ChecksumAlgorithm.NONE

    @staticmethod
    def str(alg):
        if alg is ChecksumAlgorithm.MD5:
            return "MD5"
        elif alg is ChecksumAlgorithm.SHA256:
            return "SHA256"
        else:
            return "NONE"


class ChecksumFile(object):
    """
    Checksum validation
    """

    blocksize = 65536

    def __init__(self, file_path):
        """
        Constructor takes file path as argument; checksums of different types can then be calculated for this file.
        :param file_path: Path to file
        """
        self.file_path = file_path

    def get(self, checksum_algorithm):
        """
        This function calculates the checksum using the algorithm specified by the argument 'checksum_algorithm'.
        :param checksum_algorithm: Algorithm used to create the checksum
        :return: Checksum string
        """
        hashval = None
        if checksum_algorithm == ChecksumAlgorithm.SHA256 or checksum_algorithm == 'SHA-256':
            hashval = hashlib.sha256()
        elif checksum_algorithm == ChecksumAlgorithm.MD5 or checksum_algorithm == 'MD5':
            hashval = hashlib.md5()

        with open(self.file_path, 'rb') as f:
            while True:
                buf = f.read(self.blocksize)
                if not buf:
                    break
                hashval.update(buf)
        return hashval.hexdigest()


class ChecksumValidation(object):
    """
    Checksum validation
    """

    def validate_checksum(self, file_path, checksum_expected, checksum_algorithm):
        """

        :param file_path: Path to file
        :param checksum_expected: Expected checksum
        :param checksum_algorithm: Algorithm used to create the checksum
        :return: Validity of checksum (bool)
        """
        checksum_file = ChecksumFile(file_path)
        calculated_checksum = checksum_file.get(checksum_algorithm)
        return calculated_checksum == checksum_expected


def get_sha256_hash(file):
    """
    Get SHA256 hash
    :param file: Path to file
    :return: SHA256 hash
    """
    blocksize = 65536
    hashval = hashlib.sha256()
    with open(file, 'rb') as file:
        while True:
            buf = file.read(blocksize)
            if not buf:
                break
            hashval.update(buf)
    return hashval.hexdigest()


def checksum(file_path, wd=None, alg=ChecksumAlgorithm.SHA256):
    """
    Get checksum
    :param file_path: file path
    :param wd: working directory
    :param alg: algorithm
    :return:
    """
    fp = file_path
    path = fp if wd is None else os.path.join(wd, fp)
    return ChecksumFile(path).get(alg)


def check_transfer(source, target):
    source_size = fsize(source)
    target_size = fsize(target)
    if not source_size == target_size:
        raise ValueError("Size of source file (%d bytes) and size of target file (%d bytes) are not equal" %
                         (source_size, target_size))
    if not ChecksumFile(source).get(ChecksumAlgorithm.SHA256) == ChecksumFile(target).get(ChecksumAlgorithm.SHA256):
        raise ValueError("Checksums of source %s and target %s are not equal" % (source, target))
