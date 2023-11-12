#!/usr/bin/env python
# coding=UTF-8
import configparser
import string
import subprocess

import os

from eatb import ROOT

class CliCommand(object):
    """
    CliCommand class
    Get a Command Line Interface (CLI) command based on templates defined in the configuration.
    """
    def __init__(self, name, cmd_template):
        """
        Create a command
        :param name: Command name
        :param cmd_template: Command template
        """
        self.name = name
        self.cmd_template = cmd_template

    def get_command(self, subst):
        """
        Get a Command Line Interface (CLI) command based on templates defined in the configuration.
        :param subst: Dictionary of substitution variables (e.g. {'foo': 'bar_v00000_b00001'} where 'foo' is the variable and 'bar_v00000_b00001'
        the substitution value).
        :return: list of command elements
        """
        res_cmd = []
        for cmd_part in self.cmd_template:
            if isinstance(cmd_part, string.Template):
                res_cmd.append(cmd_part.substitute(subst))
            else:
                res_cmd.append(cmd_part)
        return res_cmd


class CliExecution(object):
    """
    CliCommand class
    Get a Command Line Interface (CLI) command based on templates defined in the configuration.
    """
    def __init__(self, command):
        """
        Create a command
        :param command: Command
        """
        assert type(command) is list, "command must be of type list"
        self.command = command

    def execute(self):
        return subprocess.check_output(self.command)


class CliCommands(object):
    """
    CliCommands class
    List of CLI commands based on configuration file.
    """
    def __init__(self, commands_config_file=None):
        """
        Create commands list based on configuration file.
        :param commands_config_file: Configuration file
        """
        self.config = configparser.ConfigParser()
        self.config['DEFAULT'] = {}
        self.config.sections()
        if not commands_config_file:
            commands_config_file = os.path.join(ROOT, 'eatb/resources/default_commands.cfg')
        if not os.path.exists(commands_config_file):
            raise FileNotFoundError("Configuration not found: %s (root: %s)" % (commands_config_file, ROOT))
        self.config.read(commands_config_file)

    def get_command_template(self, command_id):
        """
        Get a Command Line Interface (CLI) command based on templates defined in the configuration.
        :param command_id: Identifier of the command
        :return: command list
        """
        command_template = self.config.get('commands', command_id)

        cmd_parts = command_template.split()

        def prep_cmd_part(cmd_part):
            if cmd_part.startswith("string.Template"):
                return eval(cmd_part)
            return cmd_part

        return [prep_cmd_part(cmd_part) for cmd_part in cmd_parts]
