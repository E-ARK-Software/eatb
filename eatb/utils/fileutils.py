import json
import os
import re
from shutil import copytree
from shutil import rmtree
import fnmatch
import shutil
import mimetypes
from urllib.parse import quote, unquote

from eatb.utils.datetime import get_file_ctime_iso_date_str, EU_UI_FORMAT, get_local_datetime_now
from eatb.utils.reporters import default_reporter

MAX_TRIES = 10000
mimetypes.add_type('text/plain', '.log')


def remove_dir(path):
    """
    Delete directory and contents (tree)
    :param path: path
    :return: success deleting directory
    """
    if os.path.isdir(path):
        rmtree(path)
        return not os.path.exists(path)


def remove_fs_item(uuid, working_dir, rel_path):
    """
    Remove file system item only if it is in a specific working directory
    :param uuid: UUID of the working direcotry
    :param working_dir: working directory
    :param rel_path: relative path within the working directory of the item to be removed
    :return: success deleting file system item
    """
    abs_path = os.path.join(working_dir, rel_path)
    if working_dir.endswith(uuid) and os.path.exists(abs_path):
        if os.path.isdir(abs_path):
            rmtree(abs_path)
        else:
            os.remove(abs_path)
    return not os.path.exists(abs_path)


def remove_protocol(path_without_protocol):
    """
    Remove protocol from path
    :param path_without_protocol:
    :return: path without protocol
    """
    protocols = ['file://', 'file:', 'file/']
    for prot in protocols:
        stripped_path = path_without_protocol.replace(prot, '')
        if len(stripped_path) < len(path_without_protocol):
            return stripped_path
    return path_without_protocol


def copy_tree_content(source_dir, target_dir):
    """
    Copy content of a directory as tree
    :param source_dir: source directory
    :param target_dir: target directory
    :return: None
    """
    fs_childs = os.listdir(source_dir)
    for fs_child in fs_childs:
        source_item = os.path.join(source_dir, fs_child)
        copytree(source_item, os.path.join(target_dir, fs_child))


def move_folder_content(source_dir, target_dir):
    """
    Move the content of a folder
    :param source_dir: source directory
    :param target_dir: target directory
    :return: None
    """
    fs_childs = os.listdir(source_dir)
    for fs_child in fs_childs:
        source_item = os.path.join(source_dir, fs_child)
        shutil.move(source_item, target_dir)


def force_merge_flat_dir(source_dir, target_dir):
    """
    Merge directories with flat structure
    :param source_dir: source directory
    :param target_dir: target directory
    :return: None
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for item in os.listdir(source_dir):
        source_file = os.path.join(source_dir, item)
        destination_file = os.path.join(target_dir, item)
        secure_force_copy_file(source_file, destination_file)


def secure_force_copy_file(source_file, target_file):
    """
    Secure file copy (checksum test)
    :param source_file:
    :param target_file:
    :return: True if target file exists and checksum verification was successful
    :raises: IOError if the checksum verification failed
    """
    if os.path.isfile(source_file):
        shutil.copy2(source_file, target_file)
        from eatb.checksum import get_sha256_hash
        if not os.path.exists(target_file) or not get_sha256_hash(source_file) == get_sha256_hash(target_file):
            raise IOError("File copy operation failed  (checksums not equal: %s vs. %s)." % (source_file, target_file))
        return os.path.exists(target_file)


def is_flat_dir(source_directory):
    """
    Check if a directory has a flat structure
    :param source_directory: Source directory
    :return: is flat directory (bool)
    """
    for item in os.listdir(source_directory):
        source_item = os.path.join(source_directory, item)
        if os.path.isdir(source_item):
            return False
    return True


def secure_copy_tree(source_file, target_file):
    """
    Secure tree copy (checksum test)
    :param source_file:
    :param target_file:
    :return: success of copying the content (bool)
    """
    for item in os.listdir(source_file):
        s = os.path.join(source_file, item)
        d = os.path.join(target_file, item)
        if os.path.isfile(s):
            if not os.path.exists(target_file):
                os.makedirs(target_file)
            secure_force_copy_file(s, d)
        if os.path.isdir(s):
            is_recursive = not is_flat_dir(s)
            if is_recursive:
                secure_copy_tree(s, d)
            else:
                force_merge_flat_dir(s, d)
    return os.path.exists(target_file)


def delete_directory_content(root_dir):
    """
    Delete content of a directory (root directory remains)
    :param root_dir:
    :return: success deleting directory content
    """
    fs_childs = os.listdir(root_dir)
    for fs_child in fs_childs:
        item = os.path.join(root_dir, fs_child)
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)
    return len(os.listdir(root_dir)) == 0


def increment_file_name_suffix(abspath_basename, extension):
    """
    Increment file name suffix
    :param abspath_basename: absolute path without extension
    :param extension: file extension
    :return: incremented file path
    """
    i = 1
    while i < MAX_TRIES:
        suffix = '%05d' % i
        inc_file_name = "%s_%s.%s" % (abspath_basename, suffix, extension)
        if not os.path.exists(inc_file_name):
            return inc_file_name
        i += 1


def latest_file_by_suffix(abspath_basename, extension):
    """
    Get latest file by suffix
    :param abspath_basename: absolute path without extension
    :param extension: file extension
    :return: incremented file path
    """
    i = 1
    file_candidate = None
    while i < MAX_TRIES:
        suffix = '%05d' % i
        inc_file_name = "%s_%s.%s" % (abspath_basename, suffix, extension)
        if not os.path.exists(inc_file_name):
            return file_candidate
        file_candidate = inc_file_name
        i += 1


def read_and_load_json_file(file_path):
    info_file_content = read_file_content(file_path)
    return json.loads(info_file_content)


def read_file_content(file_path):
    """
    Read content of a file
    :param file_path: file path
    :return: file content
    """
    mime = get_mime_type(file_path)
    mode = "r" if mime and (mime.startswith("text") or mime.endswith("json") or mime.endswith("xml")) else "rb"
    fh = open(file_path, mode)
    file_content = fh.read()
    return file_content


def locate(pattern, root_path):
    """
    Find a file within a root path
    :param pattern: Pattern (fnmatch)
    :param root_path: Root path
    :return: Generator of file list
    """
    for path, dirs, files in os.walk(os.path.abspath(root_path)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def find_files(directory, pattern):
    """
    Find files in directory (generator)
    :param directory: directory
    :param pattern: pattern (fnmatch)
    :return: Generator for list of files
    """
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def copy_file_with_base_directory(source_root, target_root, sub_path, source_file_name):
    """
    Copy file with base directory
    :param source_root: source root directory
    :param target_root: target root directory
    :param sub_path: sub-path
    :param source_file_name: source file name
    :return: success of copying the file (bool)
    """
    rel_sub_path = sub_path.lstrip("/")
    target_dir = os.path.join(target_root, rel_sub_path)
    os.makedirs(target_dir, exist_ok=True)
    source_file_path = os.path.join(source_root, rel_sub_path, source_file_name)
    target_file_path = os.path.join(target_root, rel_sub_path, source_file_name)
    shutil.copy2(source_file_path, target_file_path)
    return os.path.exists(target_file_path)


def copy_folder(source_directory, destination_directory):
    """
    Copy folder
    :param source_directory: source directory
    :param destination_directory: destination directory
    :return: success of copying directory (bool)
    """
    _, leaf_folder = os.path.split(source_directory)
    shutil.copytree(source_directory, os.path.join(destination_directory, leaf_folder))
    return os.path.exists(destination_directory)


def get_immediate_subdirectories(directory):
    """
    Get a list of sub-directories of a directory
    :param directory:
    :return: list of sub-directories
    """
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


def list_files_in_dir(directory):
    """
    List files in directory
    :param directory:
    :return:
    """
    return [name for name in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, name))]


def sub_dirs(directory):
    """
    Get a list of sub-directories of a directory
    :param directory:
    :return: list of sub-directories
    """
    return sorted([name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))])


def delete_from_dir(directory, pattern):
    """
    Delete files from a directory
    :param directory: directory
    :param pattern: pattern
    :return:
    """
    for f in os.listdir(directory):
        if re.search(pattern, f):
            path = os.path.join(directory, f)
            os.remove(path)
            if os.path.exists(path):
                return False
    return True


def purge(directory, pattern):
    """
    Delete all files from a directory
    :param directory: directory
    :param pattern: pattern
    :return:
    """
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))
    return len(os.listdir(directory)) == 0


def rec_find_files(directory, include_files_rgxs=None, exclude_dirsfiles_rgxs=None):
    """
    Find files matching pattern
    :param directory: directory where recursive search starts
    :param include_files_rgxs: regex patterns of files to be included (filter)
    :param exclude_dirsfiles_rgxs: regex patterns of directories or files to be excluded
    :return: Generator of matching files list
    """
    assert not include_files_rgxs or type(include_files_rgxs) is list, \
        "param 'includes_files' must be of type list"
    assert not exclude_dirsfiles_rgxs or type(exclude_dirsfiles_rgxs) is list, \
        "param 'excludes_dirs_files' must be of type list"
    includes_pattern = r'|'.join([x for x in include_files_rgxs]) if include_files_rgxs else None
    excludes_pattern = r'|'.join([x for x in exclude_dirsfiles_rgxs]) if exclude_dirsfiles_rgxs else None
    includes_rgxs = re.compile(includes_pattern) if includes_pattern else None
    excludes_rgxs = re.compile(excludes_pattern) if excludes_pattern else None
    for root, dirs, files in os.walk(directory):
        if not excludes_rgxs or not re.match(excludes_rgxs, root):
            if not excludes_rgxs or not re.match(excludes_rgxs, root):
                for f in files:
                    if not excludes_rgxs or not re.match(excludes_rgxs, f):
                        if not include_files_rgxs or re.match(includes_rgxs, f):
                            filename = os.path.join(root, f)
                            yield filename


def path_to_dict(path, strip_path_part=None, use_icons=False):
    d = {'text': os.path.basename(path)}
    if os.path.isdir(path.encode('utf-8')):
        if use_icons:
            d['icon'] = "glyphicon glyphicon-folder-close"
        d['children'] = [path_to_dict(os.path.join(path, x), strip_path_part) for x in sorted(os.listdir(path))]
        path_metadata = path if strip_path_part is None else path.replace(strip_path_part, "")
        d['data'] = {"path": path_metadata}
    else:
        if use_icons:
            d['icon'] = "glyphicon glyphicon-file"
        path_metadata = path if strip_path_part is None else path.replace(strip_path_part, "")
        wd_path, _ = os.path.split(path)
        mimetype = get_mime_type(path)
        mimetype = mimetype if mimetype else "application/octet-stream"
        d['data'] = {"path": path_metadata, "mimetype": mimetype,
                     "datetime": get_file_ctime_iso_date_str(path, EU_UI_FORMAT, '/var/data/earkweb')}
    return d


def total_directory_size(start_path='.'):
    """
    Get the total file size of directory and subdirectories
    :param start_path: file path
    :return: total file size of directory and subdirectories in bytes (integer value)
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def fsize(file_path, wd=None):
    """
    Get the file size of a file in the file system
    :param file_path: file path
    :param wd: working directory
    :return: file size in bytes (integer value)
    """
    fp = file_path
    path = fp if wd is None else os.path.join(wd, fp)
    return int(os.path.getsize(path))


def human_readable_size(size):
    """
    Get a fhuman readable string representation for a given file size in bytes (integer)
    :param size: size (integer)
    :return: human readable string representation of the file size
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size) < 1024.0:
            return "%3.1f%s" % (size, unit)
        size /= 1024.0


def get_mime_type(path):
    """
    Get mime type of a file
    :param path: path to file
    :return: mime type (tuple: (type, subtype))
    """
    mime_type, subtype = mimetypes.guess_type(path)
    mime_type = mime_type if mime_type else "application/octet-stream"
    return mime_type


def get_directory_json(path, subpath):
    """
    Get directory JSON representation
    :param path: path
    :param subpath: sub-path
    :return: JSON representation of directory
    """
    joined_path = os.path.join(path, subpath)
    dir_json = path_to_dict(joined_path, strip_path_part=path + '/')
    return {"data": dir_json, "check_callback": "true"}


def strip_prefixes(path, *prefixes):
    """
    Strip prefixes
    :param path: path
    :param prefixes: prefixes
    :return: String without prefixes
    """
    prefix_part = os.path.join(os.path.join(*prefixes), '')
    return path.replace(prefix_part, '')


def backup_file_path(abs_path):
    """
    Backup file path
    :param abs_path: absolute path
    :return: return path for backup
    """
    path, filename = os.path.split(abs_path)
    basename, extension = os.path.splitext(filename)
    dt = get_local_datetime_now()
    ts = dt.strftime("%Y%m%d%H%M%S")
    backup_file_name = "%s_%s%s" % (basename, ts, extension)
    return os.path.join(path, backup_file_name)


def package_sub_path_from_relative_path(root, containing_file_path, relative_path):
    """
    Get package sub-path from relative path
    param root: root path
    param containing_file_path: containing file path
    param relative_path: relative path
    :return: rpackage sub-path
    """
    containing_path, _ = os.path.split(containing_file_path)
    return strip_prefixes(os.path.abspath(os.path.join(containing_path, remove_protocol(relative_path))), root)


def get_sub_path_from_relative_path(root, containing_file_path, relative_path):
    """
    Get sub-path from relative path
    :param root: root directory
    :param containing_file_path: containing file path
    :param relative_path: relative path
    :return: sub-path
    """
    containing_path, _ = os.path.split(containing_file_path)
    return strip_prefixes(os.path.abspath(os.path.join(containing_path, relative_path)), root)

def from_safe_filename(cleaned_identifier):
    """
    Get original identifier from safe filename identifier string, see
    https://www.ietf.org/archive/id/draft-kunze-pairtree-01.txt
    :param cleaned_identifier: file name identifier string (https=+doi,org=10,5281=zenodo,4514864)
    :return: original identifier (https://doi.org/10.5281/zenodo.4514864)
    """
    # Reverse second step: single-character to single-character conversions
    translation_table = str.maketrans("=+,", "/:.")
    intermediate_identifier = cleaned_identifier.translate(translation_table)
    # Reverse first step: hexadecimal decoding
    def hex_decode(match):
        hex_value = match.group(1)
        return chr(int(hex_value, 16))
    # Replace hexadecimal encoded characters with their original characters
    original_identifier = re.sub(r'\^([0-9a-fA-F]{2})', hex_decode, intermediate_identifier)
    return original_identifier

def to_safe_filename(identifier):
    """
    Get safe filename identifier string from original identifier, see
    https://www.ietf.org/archive/id/draft-kunze-pairtree-01.txt
    :param identifier: identifier (https://doi.org/10.5281/zenodo.4514864
    :return: file name identifier string (https=+doi,org=10,5281=zenodo,4514864)
    """
    # First step: Hexadecimal encoding for special characters
    special_chars = {
        '"': '^22', '*': '^2a', '+': '^2b', ',': '^2c',
        '<': '^3c', '=': '^3d', '>': '^3e', '?': '^3f',
        '\\': '^5c', '^': '^5e', '|': '^7c', ' ': '^20'
    }
    
    def hex_encode(char):
        if char in special_chars:
            return special_chars[char]
        elif ord(char) < 0x21 or ord(char) > 0x7e:
            return f'^{ord(char):02x}'
        else:
            return char
            
    # apply conversion
    safe_identifier = ''.join(hex_encode(c) for c in identifier)
    
    # Second step: Single-character to single-character conversions
    translation_table = str.maketrans("/:.", "=+,")
    mapped_identifier = safe_identifier.translate(translation_table)
    return mapped_identifier

def encode_identifier(identifier: str) -> str:
    """
    Encode an identifier string for safe inclusion in a URL.

    :param identifier: The identifier string to be encoded.
    :return: The encoded identifier string.
    """
    return quote(to_safe_filename(identifier))


def decode_identifier(encoded_identifier: str) -> str:
    """
    Decode an identifier string for safe inclusion in a URL.

    :param encoded_identifier: The encoded identifier string to be decoded.
    :return: The decoded identifier string.
    """
    return from_safe_filename(unquote(encoded_identifier))

class FileBinaryDataChunks(object):
    """
    Generator to iteratively read binary chunks of a large file
    """

    def __init__(self, filepath, chunksize=65536, progress_reporter=default_reporter):
        """
        Initialise object with file path and chunksize
        :param filepath: File path
        :param chunksize: Chunk size
        """
        self.filepath = filepath
        self.chunksize = chunksize
        self.progress_reporter = progress_reporter
        self.current_file_size = os.path.getsize(filepath)
        self.bytesread = 0

    def chunks(self, total_bytes_read=0, bytes_total=-1):
        """
        Chunk generator, returns data chunks which can be iterated in a for loop.
        :return: generator with data chunks
        """
        if bytes_total == -1:
            bytes_total = self.current_file_size
        f = open(self.filepath, 'rb')

        def readchunk():
            return f.read(self.chunksize)

        for chunk in iter(readchunk, ''):
            self.bytesread += len(chunk)
            percent = (total_bytes_read+self.bytesread) * 100 / bytes_total
            self.progress_reporter(percent)
            yield chunk


def copy_file(source, target, progress_reporter=default_reporter, total_bytes_read=0):
    with open(target, 'wb') as target_file:
        for chunk in FileBinaryDataChunks(source, 65536, progress_reporter).chunks(total_bytes_read, total_bytes_read):
            target_file.write(chunk)
        target_file.close()
        total_bytes_read += fsize(source)
    return total_bytes_read
