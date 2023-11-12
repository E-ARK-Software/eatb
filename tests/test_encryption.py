#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import unittest

from eatb import ROOT
from eatb.cli import CliCommand, CliCommands
from eatb.utils import randomutils
from eatb.utils.encrypt import gpg_encrypt_file_passphrase
from eatb.utils.fileutils import read_file_content


class EncryptionTest(unittest.TestCase):

    test_file = 'test.txt'
    test_dir = os.path.join(ROOT, 'tests/test_resources')
    test_file_path = os.path.join(test_dir, test_file)
    tmp_dir = '/tmp/temp-' + randomutils.randomword(10)
    tmp_file_path = os.path.join(tmp_dir, test_file)

    def setUp(self):
        os.makedirs(EncryptionTest.tmp_dir, exist_ok=True)
        shutil.copyfile(EncryptionTest.test_file_path, EncryptionTest.tmp_file_path)

    def tearDown(self):
        shutil.rmtree(EncryptionTest.tmp_dir)

    def test_gpg_encrypt_file_passphrase(self):
        """
        Test encrypt/decrypt with passphrase
        """
        cmd_encrypt = gpg_encrypt_file_passphrase(EncryptionTest.test_file, "12345")
        print(cmd_encrypt)
        self.assertEqual(7, len(cmd_encrypt))
        expected_cmd_list = ['gpg', '--yes', '--batch', '--passphrase', '12345', '-c', EncryptionTest.test_file]
        self.assertTrue(cmd_encrypt == expected_cmd_list)
        out = subprocess.call(cmd_encrypt, cwd=EncryptionTest.tmp_dir)
        self.assertEqual(0, out)
        cli_commands = CliCommands()
        cli_command = CliCommand("gpg_passphrase_decrypt_file", cli_commands.get_command_template("gpg_passphrase_decrypt_file"))
        cmd_decrypt = cli_command.get_command({'encrypted_file': "%s.gpg" % EncryptionTest.test_file,
                                               'decrypted_file': "test_decrypted.txt", 'passphrase': "12345"})
        out = subprocess.call(cmd_decrypt, cwd=EncryptionTest.tmp_dir)
        self.assertEqual(0, out)
        self.assertEqual("test", read_file_content(os.path.join(EncryptionTest.tmp_dir,"test_decrypted.txt")))


if __name__ == '__main__':
    unittest.main()
