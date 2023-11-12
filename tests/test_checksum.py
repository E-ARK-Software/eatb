#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from eatb import ROOT
from eatb.checksum import ChecksumFile, ChecksumValidation, ChecksumAlgorithm


class TestChecksum(unittest.TestCase):

    test_dir = os.path.join(ROOT, 'tests/test_resources/')
    test_file = test_dir + 'test.txt'
    csobj = ChecksumFile(test_file)
    csval = ChecksumValidation()

    def test_get_MD5(self):
        """
         Checksum (type MD5) must return SHA256 checksum value
        """
        actual = self.csobj.get(ChecksumAlgorithm.MD5)
        self.assertTrue(actual is not None, "Checksum (type MD5) must not be empty")
        self.assertEqual(actual, "098f6bcd4621d373cade4e832627b4f6")

    def test_get_SHA256(self):
        """
        Checksum (type SHA256) must return SHA256 checksum value
        """
        actual = self.csobj.get(ChecksumAlgorithm.SHA256)
        self.assertTrue(actual is not None, "Checksum (type SHA256) must not be empty")
        self.assertEqual(actual, "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")

    def test_validate_valid_MD5(self):
        """
        Must validate a correct MD5 checksum
        """
        expected = "098f6bcd4621d373cade4e832627b4f6"
        actual = self.csval.validate_checksum(self.test_file, expected, ChecksumAlgorithm.MD5)
        self.assertTrue(actual, "Must validate a correct MD5 checksum")

    def test_notvalidate_invalid_MD5(self):
        """
        Must validate a correct MD5 checksum
        """
        expected = "incorrect_md5"
        actual = self.csval.validate_checksum(self.test_file, expected, ChecksumAlgorithm.MD5)
        self.assertFalse(actual, "Must not validate an incorrect MD5 checksum")

    def test_validate_valid_SHA256(self):
        """
        Must validate a correct SHA256 checksum
        """
        expected = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        actual = self.csval.validate_checksum(self.test_file, expected, ChecksumAlgorithm.SHA256)
        self.assertTrue(actual, "Must validate a correct SHA256 checksum")

    def test_notvalidate_invalid_SHA256(self):
        """
        Must validate a correct SHA256 checksum
        """
        expected = "incorrect_sha256"
        actual = self.csval.validate_checksum(self.test_file, expected, ChecksumAlgorithm.SHA256)
        self.assertFalse(actual, "Must not validate an incorrect SHA256 checksum")


if __name__ == '__main__':
    unittest.main()
