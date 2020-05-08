#!/usr/bin/env python
# coding=UTF-8
import sys

class CC:
    def __init__(self):
        pass
    HEADER = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_headline(headline):
    print("%s====================================================================%s" % (CC.HEADER, CC.ENDC))
    print("%s%s%s" % (CC.HEADER, headline, CC.ENDC))
    print("%s====================================================================%s" % (CC.HEADER, CC.ENDC))


def success(msg):
    print("%s%s%s" % (CC.OKGREEN, msg, CC.ENDC))


def failure(msg):
    print("%s%s%s" % (CC.FAIL, msg, CC.ENDC))
    sys.exit(1)


def warning(msg):
    print("%s%s%s" % (CC.WARNING, msg, CC.ENDC))
