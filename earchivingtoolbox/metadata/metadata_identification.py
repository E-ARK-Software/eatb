#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402

from lxml import etree


def MetaIdentification(unknown_xml):
    parsed_unknown = etree.parse(unknown_xml)
    unknown_tag =  parsed_unknown.getroot().tag
    tag = unknown_tag.split('}')
    if len(tag) == 2:
        return tag[1]
    elif len(tag) == 1:
        return tag[0]
