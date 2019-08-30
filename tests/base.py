import unittest
import tarfile
import sys
from os import listdir

IP_compressed_path = '/home/matteo/eARK/earkweb/earkresources/AIP-test/siardpackage/SIA_test_animals_2.tar'
rules_path = './rules.xml'


class Base(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if not tarfile.is_tarfile(IP_compressed_path):
            print('Format not supported')
            print('Provided IP path:', IP_compressed_path)
            sys.exit()
        self.IP_compressed_path = IP_compressed_path
        self.IP_path = IP_compressed_path.split('/')[-1].split('.')[0]
        if self.IP_path not in listdir('.'):
            print('Extracting')
            with tarfile.open(IP_compressed_path) as tf:
                tf.extractall(self.IP_path)
        with open(rules_path) as fp:
            xml_rules = fp.read()
        self.rules_lines = xml_rules.split('\n')
