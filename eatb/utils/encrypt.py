import unittest

from eatb.cli.cli import CliCommand


def gpg_encrypt_file_passphrase(file, passphrase):
    return CliCommand.get_command("gpg_passphrase_encrypt_file", {'file': file, 'passphrase': passphrase})



class CliCommandTest(unittest.TestCase):
    def test_gpg_encrypt_file_passphrase(self):
        """
        Must return CLI command
        """
        cmd = gpg_encrypt_file_passphrase("test.txt", "12345")
        print(cmd)
        #out = subprocess32.call(cmd, cwd=os.path.join(root_dir,"testresources"))
        #self.assertEqual(0, out)
        # cmd = CliCommand.get("gpg_passphrase_decrypt_file",
        #                      {'encrypted_file': "test.txt.gpg", 'decrypted_file': "test_decrypted.txt", 'passphrase': "12345"})
        # out = subprocess32.call(cmd, cwd=os.path.join(root_dir,"testresources"))
        # self.assertEqual(0, out)
        # self.assertEqual("test", read_file_content(os.path.join(root_dir,"testresources/test_decrypted.txt")))
        # os.remove(os.path.join(root_dir,"testresources/test.txt.gpg"))
        # os.remove(os.path.join(root_dir,"testresources/test_decrypted.txt"))




if __name__ == '__main__':
    unittest.main()
