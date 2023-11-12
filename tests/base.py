import os
import unittest
import tarfile
import sys
from eatb.utils.randomutils import randomword
from eatb import ROOT

IP_path = os.path.join(ROOT, 'tests/test_resources/minimal_IP_with_schemas')
rules_path = os.path.join(ROOT, 'tests/test_resources/rules.xml')


class Base(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.IP_path = IP_path
        with open(rules_path) as fp:
            xml_rules = fp.read()
        self.rules_lines = xml_rules.split('\n')
