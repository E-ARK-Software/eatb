#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import generators

import logging
import os
import re
import sys
import tarfile
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from subprocess import check_output
from eatb.cli import CliCommands, CliCommand
from eatb.checksum import ChecksumFile, ChecksumAlgorithm
from eatb.utils.reporters import default_reporter


class ManifestCreation():
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
        out = check_output(command)
        return out


def create_package(input_directory, packagename, gunzip=False, output_directory=None, use_input_dir_as_root=False, exclude=[]) -> str:
    """
    Create package
    :param input_directory: Input directory
    :param packagename: Name of the package file
    :param output_directory: Output directory (same as input directory if not provided)
    :gunzip create compressed container package
    :return: md5checksum of package
    """

    # append generation number to tar file; if tar file exists, the generation number is incremented
    input_path = Path(input_directory)
    extension = '.tar.gz' if gunzip else '.tar'
    if not output_directory:
        output_directory = input_path.parent
    storage_tar_file = os.path.join(output_directory, packagename + extension)
    write_mode = "w:gz" if gunzip else "w:"
    tar = tarfile.open(storage_tar_file, "w:")
    total = sum([len(files) for (root, dirs, files) in os.walk(input_directory)])
    i = 0
    for subdir, dirs, files in os.walk(input_directory):

        for dir in dirs:
            entry = os.path.join(os.path.basename(input_directory), subdir, dir)
            base = os.path.basename(input_directory) if use_input_dir_as_root else ""
            if not os.listdir(entry):
                tar.add(entry, arcname=os.path.join(base, os.path.relpath(entry, input_directory)))

        for file in files:
            entry = os.path.join(os.path.basename(input_directory), subdir, file)
            base = os.path.basename(input_directory) if use_input_dir_as_root else ""

            def exclude_func(file_name):
                return os.path.basename(file_name) in exclude

            tar.add(entry, arcname=os.path.join(base, os.path.relpath(entry, input_directory)))
            if i % 10 == 0:
                perc = (i * 100) / total
            i += 1
    tar.close()

    checksum_file = ChecksumFile(storage_tar_file)
    return checksum_file.get(ChecksumAlgorithm.MD5)


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


class ChunkedTarEntryReader(object):
    """
    Chunked TAR entry reader allowing to read large TAR entries.
    """

    def __init__(self, tfile: tarfile, chunksize: int = 512):
        self.tfile = tfile
        self.chunksize = chunksize
        self.bytesread = 0

    def close(self):
        if self.tfile:
            return self.tfile.close()
        return True

    def chunks(self, entry, total_bytes_read=0, bytes_total=-1):
        """
        Chunk generator, returns data chunks which can be iterated in a for loop.
        :return: generator with data chunks
        """
        tinfo = self.tfile.getmember(entry)

        if bytes_total == -1:
            bytes_total = tinfo.size
        f = self.tfile.extractfile(tinfo)

        def readchunk():
            return f.read(self.chunksize)

        for chunk in iter(readchunk, ''):
            self.bytesread += len(chunk)
            percent = (total_bytes_read+self.bytesread) * 100 / bytes_total
            default_reporter(percent)
            yield chunk
            if percent == 100:
                break

def get_deliveries(path, task_logger):
    package_files = [f for f in os.listdir(path) if re.search(r'.*\.(zip|tar)$', f)]
    task_logger.addinfo("Package files found: %s" % package_files)
    deliveries = {}
    for package_file in package_files:
        tar_base_name, _ = os.path.splitext(package_file)
        delivery_file = os.path.join(path, ("%s.xml" % tar_base_name))
        task_logger.addinfo("Looking for delivery file: %s" % delivery_file)
        if os.path.exists(delivery_file):
            deliveries[tar_base_name] = {"delivery_xml": delivery_file, "package_file": package_file}
        else:
            task_logger.addinfo("Warning: no delivery file found for package: %s" % tar_base_name)
    return deliveries
