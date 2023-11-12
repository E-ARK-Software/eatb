#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from subprocess import check_output

from eatb.cli import CliCommand, CliCommands


def get_hashed_filelist(strip_path_part, directory, commands=CliCommands()):
    """
    e.g. get_hashed_filelist("/home/user/", "/home/user/test")
    :param commands:
    :param strip_path_part: part of the path to be removed for the key
    :param directory: directory for which the hashed file list is to be created
    :return: hashed file list
    """
    cli_command = CliCommand("summainstdout", commands.get_command_template("summainstdout"))
    command = cli_command.get_command(dict(package_dir=directory))
    summain_out = check_output(command)
    json_summain_out = json.loads(summain_out)
    result = {}
    for entry in json_summain_out:
        if "SHA256" in entry:
            key = entry['Name'].lstrip(strip_path_part)
            result[key] = {"hash": entry['SHA256'], "path": entry["Name"]}
    return result


