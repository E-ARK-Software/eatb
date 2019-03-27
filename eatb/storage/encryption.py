from eatb.cli.cli import CliCommand, CliCommands


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


