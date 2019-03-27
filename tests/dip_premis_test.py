#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import unittest

from eatb import root_dir
from eatb.metadata.premis.dippremis import DIPPremis


class DIPPremisTest(unittest.TestCase):

    test_premis = os.path.join(root_dir, 'tests/test_resources/metadata/premis/premis.xml')

    def test_add_related_aips(self):
        """
        Test premis manipulation.
        """
        dip_premis = DIPPremis(DIPPremisTest.test_premis)
        dip_premis.add_related_aips(['d6e09e6a-5029-4273-99ef-f2307926379b',
                                     'd6e09e6a-5029-4273-99ef-f2307926379c'],
                                    'DIPAcquireAIPs')
        self.assertIsNotNone(dip_premis)


if __name__ == '__main__':
    unittest.main()
