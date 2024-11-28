#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test vocabulary parsing"""
import os
import json
import unittest
from eatb import ROOT
from eatb.utils.xmlutils import parse_csip_vocabulary

VOCABULARY_TEST_RESOURCES = os.path.join(ROOT, 'tests/../eatb/resources/vocabularies/')
CONTENT_CATEGORY_VOCABULARY = os.path.join(VOCABULARY_TEST_RESOURCES, 'CSIPVocabularyContentCategory.xml')

class TestOcflStorage(unittest.TestCase):
    """Test storage functions"""
    content_category_vocabulary = {}
    content_category_terms = []
    @classmethod
    def setUpClass(cls):
        # Read and parse the XML file
        with open(CONTENT_CATEGORY_VOCABULARY, 'r', encoding='utf-8') as file:
            TestOcflStorage.content_category_vocabulary = parse_csip_vocabulary(file)
        with open(CONTENT_CATEGORY_VOCABULARY, 'r', encoding='utf-8') as file:
            TestOcflStorage.content_category_terms = parse_csip_vocabulary(file, terms_only=True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_terms_only(self):
        """Test getting term list"""
        print(json.dumps(TestOcflStorage.content_category_vocabulary, indent=4))
        print(json.dumps(TestOcflStorage.content_category_terms, indent=4))
        self.assertTrue(len(TestOcflStorage.content_category_terms) > 1)


if __name__ == '__main__':
    unittest.main()
