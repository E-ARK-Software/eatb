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
            tf.extractall("./")
        with open(rules_path) as fp:
            xml_rules = fp.read()
        self.rules_lines = xml_rules.split('\n')
