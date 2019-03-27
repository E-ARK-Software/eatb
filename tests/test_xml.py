#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import unittest

import lxml.etree as ET

from eatb import root_dir
from eatb.utils.fileutils import read_file_content
from eatb.xml.deliveryvalidation import DeliveryValidation
from eatb.xml.xmlutils import get_dcat_element_values

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402


class TestXml(unittest.TestCase):

    test_dir = root_dir + '/testresources/'
    delivery_dir = os.path.join(root_dir, 'tests/test_resources/Delivery-test/')

    schema_file = delivery_dir + 'schemas/IP.xsd'
    package_file = delivery_dir + 'pkg.tar.gz'
    vsip = DeliveryValidation()

    def test_get_dataset_property_value(self):
        """
        Test get dataset property value
        """
        md_file = os.path.join(root_dir + '/tests/test_resources/metadata/dcat/dcat2.xml')
        substitutions = {
            "//*/dcat:dataset/dcat:Dataset/dct:identifier": "xxx",
            "//*/dcat:dataset/dcat:Dataset/dcat:accessURL": "yyy",
            "//*/dcat:dataset/dcat:Dataset/dcat:distribution/dcat:Distribution/dcat:accessURL": "zzz"
        }
        xml_content = read_file_content(md_file)
        tree = ET.XML(xml_content.encode('utf-8'))
        distributions = set(tree.xpath("//*/dcat:dataset/dcat:Dataset/dcat:distribution/dcat:Distribution/dcat:accessURL", namespaces={'dct': 'http://purl.org/dc/terms/',
                                                                  'dcat': 'http://www.w3.org/ns/dcat#'}))

        changed_cont = get_dcat_element_values(md_file, substitutions)

        print(changed_cont)


if __name__ == '__main__':
    unittest.main()
