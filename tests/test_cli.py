#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import unittest

from eatb.cli import CliCommand, CliCommands
from eatb.cli import CliExecution


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
