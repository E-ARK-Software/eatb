import unittest

from eatb.cli import CliCommand, CliCommands


def gpg_encrypt_file_passphrase2(file, passphrase):
    return CliCommand.get_command("gpg_passphrase_encrypt_file", {'file': file, 'passphrase': passphrase})


def gpg_encrypt_file_passphrase(file, passphrase):
    """
    Encrypt file using passphrase
    :param file: file
    :param passphrase: passphrase
    :return: CLI command string
    """
    cli_commands = CliCommands()
    cli_command = CliCommand("gpg_passphrase_encrypt_file", cli_commands.get_command_template("gpg_passphrase_encrypt_file"))
    command = cli_command.get_command({'file': file, 'passphrase': passphrase})
    return command




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
