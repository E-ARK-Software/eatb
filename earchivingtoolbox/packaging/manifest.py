#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402
from subprocess import check_output
from earchivingtoolbox.cli.cli import CliCommands
from earchivingtoolbox.cli.cli import CliCommand



class ManifestCreation(object):
    """
    Create package file manifest using 'summain'
    """
    def __init__(self, working_directory, commands=CliCommands()):
        self.working_directory = working_directory
        self.commands = commands
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)

    def create_manifest(self, package_dir, manifest_file):
        cli_command = CliCommand("summain", self.commands.get_command_template("summain"))
        command = cli_command.get_command(dict(manifest_file=manifest_file, package_dir=package_dir))
        print(command)
        out = check_output(command)
        return out
