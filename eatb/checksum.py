#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import os

from eatb import logger
from eatb.utils.fileutils import fsize


class ChecksumAlgorithm:
    """
    Checksum algorithm
    """
    MD5, SHA256, SHA512, NONE = range(4)

    @staticmethod
    def get(alg):
        """
        Get algorithm by string
        :param alg: Algorithm string
        :return: Checksum algorithm
        """
        if alg.lower() == "md5":
            return ChecksumAlgorithm.MD5
        if alg.lower() == "sha256" or alg.lower() == "sha-256":
            return ChecksumAlgorithm.SHA256
        if alg.lower() == "sha256" or alg.lower() == "sha-256":
            return ChecksumAlgorithm.SHA512
        return ChecksumAlgorithm.NONE

    @staticmethod
    def str(alg):
        if alg is ChecksumAlgorithm.MD5:
            return "MD5"
        if alg is ChecksumAlgorithm.SHA256:
            return "SHA256"
        if alg is ChecksumAlgorithm.SHA256:
            return "SHA512"
        return "NONE"


class ChecksumFile():
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
        if checksum_algorithm in [ChecksumAlgorithm.SHA256, 'SHA-256']:
            hashval = hashlib.sha256()
        if checksum_algorithm in [ChecksumAlgorithm.SHA512, 'SHA-512']:
            hashval = hashlib.sha512()
        elif checksum_algorithm in [ChecksumAlgorithm.MD5, 'MD5']:
            hashval = hashlib.md5()

        with open(self.file_path, 'rb') as f:
            while True:
                buf = f.read(self.blocksize)
                if not buf:
                    break
                hashval.update(buf)
        return hashval.hexdigest()


class ChecksumValidation():
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


def get_hash(file, checksum_algorithm):
    """
    Get MD5/SHA256/SHA512 hash
    :param file: Path to file
    :return: MD5/SHA256/SHA512 hash
    """
    blocksize = 65536
    hashval = None
    if checksum_algorithm in [ChecksumAlgorithm.SHA256, 'SHA-256']:
        hashval = hashlib.sha256()
    if checksum_algorithm in [ChecksumAlgorithm.SHA512, 'SHA-512']:
        hashval = hashlib.sha512()
    elif checksum_algorithm in [ChecksumAlgorithm.MD5, 'MD5']:
        hashval = hashlib.md5()
    with open(file, 'rb') as file:
        while True:
            buf = file.read(blocksize)
            if not buf:
                break
            hashval.update(buf)
    return hashval.hexdigest()


def get_hash_values(file):
    """
    Get MD5/SHA256/SHA512 hash
    :param file: Path to file
    :return: MD5/SHA256/SHA512 hash
    """
    blocksize = 65536
    hashval_sha256 = hashlib.sha256()
    hashval_md5 = hashlib.md5()
    hashval_sha512 = hashlib.sha512()
    with open(file, 'rb') as file:
        while True:
            buf = file.read(blocksize)
            if not buf:
                break
            hashval_md5.update(buf)
            hashval_sha256.update(buf)
            hashval_sha512.update(buf)
    return hashval_md5.hexdigest(), hashval_sha256.hexdigest(), hashval_sha512.hexdigest()

def get_md5_hash(file):
    """
    Get MD5 hash
    :param file: Path to file
    :return: MD5 hash
    """
    return get_hash(file, ChecksumAlgorithm.MD5)


def get_sha256_hash(file):
    """
    Get SHA256 hash
    :param file: Path to file
    :return: SHA256 hash
    """
    return get_hash(file, ChecksumAlgorithm.SHA256)


def get_sha512_hash(file):
    """
    Get SHA512 hash
    :param file: Path to file
    :return: SHA512 hash
    """
    return get_hash(file, ChecksumAlgorithm.SHA512)


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
    """
    Check successful transfer by comparing checksum values and file sizes of source and target
    :param file_path: file path
    :param wd: working directory
    :param alg: algorithm
    :except Different file sizes or checksum values
    :return: None
    """
    source_size = fsize(source)
    target_size = fsize(target)
    if not source_size == target_size:
        raise ValueError("Size of source file (%d bytes) and size of target file (%d bytes) are not equal" %
                         (source_size, target_size))
    if not ChecksumFile(source).get(ChecksumAlgorithm.SHA256) == ChecksumFile(target).get(ChecksumAlgorithm.SHA256):
        raise ValueError("Checksums of source %s and target %s are not equal" % (source, target))


def files_identical(file1, file2):
    if not (os.path.exists(file1) and os.path.exists(file2)):
        logger.error("Files must both exist to verify if they are identical: %s, %s" % (file1, file2))
        return False
    checksum_source_file = ChecksumFile(file1).get('SHA-256')
    checksum_target_file = ChecksumFile(file2).get('SHA-256')
    logger.debug("f1: %s, f2: %s" % (file1, file2))
    logger.debug("cs1: %s, cs2: %s" % (checksum_source_file, checksum_target_file))
    return checksum_source_file == checksum_target_file
