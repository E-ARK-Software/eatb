import unittest
import tarfile
import sys

IP_compressed_path = './tests/test_resources/minimal_IP_with_schemas.tar'
rules_path = './tests/rules.xml'

class Base(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if not tarfile.is_tarfile(IP_compressed_path):
            print('Format not supported')
            print('Provided IP path:', IP_compressed_path)
            sys.exit()
        self.IP_compressed_path = IP_compressed_path
        self.IP_path = IP_compressed_path.split('/')[-1].split('.')[0]
        print('Extracting')
        with tarfile.open(IP_compressed_path) as tf:
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tf, "./")
        with open(rules_path) as fp:
            xml_rules = fp.read()
        self.rules_lines = xml_rules.split('\n')
