#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import string
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
from eatb.cli.cli import CliCommand, CliCommands
from eatb.cli.cli import CliExecution


class CliCommandTest(unittest.TestCase):

    def test_get_cli_command(self):
        cli_command = CliCommand("echo", ['echo', string.Template('$input')])
        command = cli_command.get_command({'input': 'foo'})
        cli_execution = CliExecution(command)
        process_output = cli_execution.execute()
        print(process_output)

    def test_cli_commands(self):
        cli_commands = CliCommands()
        cli_command = CliCommand("echo", cli_commands.get_command_template("echo"))
        command = cli_command.get_command({'input': "test"})
        self.assertIsNotNone(command)
        self.assertEqual(2, len(command))
        self.assertEqual('echo', command[0])
        self.assertEqual('test', command[1])


if __name__ == '__main__':
    unittest.main()
