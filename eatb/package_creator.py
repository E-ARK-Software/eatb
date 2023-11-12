#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Command line utility for creating E-ARK Submission and Archival IPs. """
import argparse
import os
import uuid

# using absolute imports, therefore adding root to python path
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")) # NOQA

from eatb import LOGGER
from eatb.oais_ip import create_sip, OAISPackageType, create_aip


def main():

    parser = argparse.ArgumentParser(description='eArchiving Toolbox - command line interface (CLI).')

    parser.add_argument('--name', "-n", type=str, help='Information package name', required=True)
    parser.add_argument('--directory', "-d", type=str, help='Information package content directory', required=True)
    parser.add_argument('--premis', "-p", action='store_true', help='Generate premis skeleton')
    parser.add_argument('--type', "-t", type=str, default="SIP",
                        choices=["SIP", "AIP"], help="Package type")
    parser.add_argument('--identifier', "-i", default=uuid.uuid4().__str__(), help='Identifier (default: generated)')
    parser.add_argument('--package', "-c", action='store_true', help='Create TAR package', default=True)
    args = parser.parse_args()

    if not os.path.exists(args.directory):
        msg = "The directory does not exist: %s" % args.directory
        LOGGER.error(msg)
        raise FileNotFoundError(msg)

    if not (os.path.isabs(args.directory)):
        msg = "The directory must be provided as absolute path: %s" % args.directory
        LOGGER.error(msg)
        raise ValueError(msg)

    if OAISPackageType[args.type] == OAISPackageType.SIP and create_sip(args.directory, args.name, args.identifier):
        LOGGER.info("SIP created successfully")
    elif OAISPackageType[args.type] == OAISPackageType.AIP and create_aip(args.directory, args.name, args.identifier):
        LOGGER.info("AIP created successfully")
    else:
        LOGGER.error("Package type not supported")


if __name__ == '__main__':
    main()
