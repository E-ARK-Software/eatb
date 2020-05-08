#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import generators

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
        if filename.endswith("tar"):
            return PackageFormat.TAR
        if filename.endswith("zip"):
            return PackageFormat.ZIP
        return PackageFormat.NONE

    @staticmethod
    def str(alg):
        if alg is PackageFormat.TARGZ:
            return "TARGZ"
        if alg is PackageFormat.TAR:
            return "TAR"
        if alg is PackageFormat.ZIP:
            return "ZIP"
        return "NONE"
