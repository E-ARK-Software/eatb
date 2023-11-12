#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

try:
    from fido.fido import Fido
    fido_disabled = False
except ImportError:
    fido_disabled = True

from eatb import ROOT
from eatb.file_format import FormatIdentification


class TestFormatIdentification(unittest.TestCase):

    def testFido(self):
        if not fido_disabled:
            ffid = FormatIdentification()
            puid = ffid.identify_file(os.path.join(ROOT, "tests/test_resources/schemas/xlink.xsd"))
            self.assertTrue("x-fmt/280", puid)
            self.assertEqual("application/xml", ffid.get_mime_for_puid(puid))
        else:
            print("Note: Fido module is not available!")


if __name__ == '__main__':
    unittest.main()
