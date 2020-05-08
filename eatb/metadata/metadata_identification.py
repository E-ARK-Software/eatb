#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import etree

def MetaIdentification(unknown_xml):
    parsed_unknown = etree.parse(unknown_xml)
    unknown_tag =  parsed_unknown.getroot().tag
    tag = unknown_tag.split('}')
    if len(tag) == 2:
        return tag[1]
    if len(tag) == 1:
        return tag[0]
