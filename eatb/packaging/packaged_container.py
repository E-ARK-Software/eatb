#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import logging
import os
import sys
import tarfile
import zipfile

from eatb.packaging.package_format import PackageFormat
from eatb.utils.reporters import default_reporter

logger = logging.getLogger(__name__)

class PackagedContainer(ABC):

    def __init__(self, container_file, stream=None):
        self.container_file = container_file
        if stream is None:
            self.stream = stream if stream else sys.stdout
        self.success = False
        self.percent = 0
        self.number_of_items = 0

    @abstractmethod
    def extract(self, extract_to):
        pass

    @staticmethod
    def factory(filename):
        if PackageFormat.get(filename) == PackageFormat.TAR or PackageFormat.get(filename) == PackageFormat.TARGZ:
            return TarContainer(filename)
        if PackageFormat.get(filename) == PackageFormat.ZIP:
            return ZipContainer(filename)
        assert 0, "Package format not supported"

class TarContainer(PackagedContainer):
    """
    Extract TAR container
    """

    def __init__(self, container_file, stream=None):
        super().__init__(container_file, stream)

    def extract(self, extract_to):
        """
        This function extracts a SIP file to a target directory.
        :param package_file_path: package file path
        :param extract_to: target directory
        :return:
        """
        total = 0
        try:
            tar_object = tarfile.open(name=self.container_file, mode='r', encoding='utf-8')
            members = tar_object.getmembers()
            total = len(members)
            print("Total: " + str(total))
            i = 100
            for member in members:
                if i % 100 == 0:
                    perc = (i*100)/total
                    logger.debug("100 processed (item %d) ... (%d)" % (i, perc))
                tar_object.extract(member, extract_to)
                i += 1
        except (ValueError, OSError, IOError, tarfile.TarError) as why:
            logger.error('Problem to extract %s' % self.container_file, why)
        return total

    def has_member(self, package_file_path, member_name):
        tar_object = tarfile.open(name=package_file_path, mode='r', encoding='utf-8')
        try:
            tar_object.getmember(member_name)
            return True
        except KeyError:
            return False

    def extract_with_report(self, package_file_path, extract_to, progress_reporter=default_reporter,
                            total=0, current=0):
        try:
            logger.info("Extracting package %s to %s" % (package_file_path, extract_to))
            tar_object = tarfile.open(name=package_file_path, mode='r', encoding='utf-8')
            members = tar_object.getmembers()
            total = len(members)
            for member in members:
                if current % 2 == 0:
                    perc = (current * 100) / total
                    progress_reporter(perc)
                tar_object.extract(member, extract_to)
                current += 1
        except (ValueError, OSError, IOError, tarfile.TarError) as why:
            logger.error('Problem to extract %s' % package_file_path, why)
        return total


class ZipContainer(PackagedContainer):

    def __init__(self, container_file, stream=None):
        super().__init__(container_file, stream)

    def extract(self, extract_to):
        return self.unzip(extract_to)

    def unzip(self, directory, progress_reporter=default_reporter):
        self.percent = 10
        try:
            if not directory.endswith(':') and not os.path.exists(directory):
                os.mkdir(directory)

            zf = zipfile.ZipFile(self.container_file)

            # create directory structure
            self._createstructure(self.container_file, directory)

            num_files = len(zf.namelist())
            self.number_of_items = num_files

            self.stream.write("Extracting %s items (directories and files)\n" % num_files)

            percent = self.percent
            divisions = 100 / percent

            percent = int(num_files / divisions)

            # extract files to directory structure
            for i, name in enumerate(zf.namelist()):
                if percent > 0 and (i % percent) == 0 and i > 0:
                    complete = int(i / percent) * percent
                    progress_reporter(complete)

                if not name.endswith('/'):
                    outfile = open(os.path.join(directory, name), 'wb')
                    outfile.write(zf.read(name))
                    outfile.flush()
                    outfile.close()
            num_f = sum([len(files) for r, d, files in os.walk(directory)])
            self.stream.write("Extracted %s files\n" % num_f)
            self.success = True
        except ValueError as e:
            self.stream.write('Problem to extract %s: %s\n' % (self.container_file, str(e)))
            self.success = False
        except OSError as e:
            self.stream.write('Problem to extract %s: %s\n' % (self.container_file, str(e)))
            self.success = False
        except IOError as e:
            self.stream.write('Problem to extract %s: %s\n' % (self.container_file, str(e)))
            self.success = False
        return self.success

    @staticmethod
    def has_member(package_file_path, member_name):
        zf = zipfile.ZipFile(package_file_path)
        return member_name in zf.namelist()

    def _createstructure(self, file, directory):
        self._makedirs(self._listdirs(file), directory)

    @classmethod
    def _makedirs(cls, directories, basedir):
        """ Create directories """
        for directory in directories:
            curdir = os.path.join(basedir, directory)
            if not os.path.exists(curdir):
                os.makedirs(curdir)
                print(curdir)

    @classmethod
    def _listdirs(cls, file):
        """ Get the directories """
        zf = zipfile.ZipFile(file)
        dirs = []
        filelist = filter(lambda x: not x.endswith('/'), zf.namelist())
        dirlist = filter(lambda x: x.endswith('/'), zf.namelist())
        for f in filelist:
            path, filename = os.path.split(f)
            if path.startswith("/"):
                path = path[1:len(path)]
            dirs.append(path)
        dirs.extend(dirlist)
        dirs.sort()
        return dirs
