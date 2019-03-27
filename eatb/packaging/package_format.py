#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import generators
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402


class PackageFormat:
    TARGZ, TAR, ZIP, NONE = range(4)

    @staticmethod
    def get(filename):
        """
        Constructor
        :param filename: filename
        :return:  Package Format
        """
        if filename.endswith("tar.gz"):
            return PackageFormat.TARGZ
        elif filename.endswith("tar"):
            return PackageFormat.TAR
        elif filename.endswith("zip"):
            return PackageFormat.ZIP
        else:
            return PackageFormat.NONE

    @staticmethod
    def str(alg):
        if alg is PackageFormat.TARGZ:
            return "TARGZ"
        elif alg is PackageFormat.TAR:
            return "TAR"
        elif alg is PackageFormat.ZIP:
            return "ZIP"
        else:
            return "NONE"
