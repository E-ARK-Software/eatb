#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import unittest
try:
    from fido.fido import Fido
    fido_disabled = False
except ImportError:
    fido_disabled = True
from earchivingtoolbox.format.formatidentification import FormatIdentification
from earchivingtoolbox import root_dir


class TestFormatIdentification(unittest.TestCase):

    def testFido(self):
        if not fido_disabled:
            ffid = FormatIdentification()
            puid = ffid.identify_file(os.path.join(root_dir, "tests/test_resources/schemas/xlink.xsd"))
            self.assertTrue("x-fmt/280", puid)
            self.assertEqual("application/xml", ffid.get_mime_for_puid(puid))
        else:
            print("Note: Fido module is not available!")


if __name__ == '__main__':
    unittest.main()
