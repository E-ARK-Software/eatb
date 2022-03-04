#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path

from lxml import etree

from eatb import ROOT
from eatb.metadata.mets.metsgenerator import MetsGenerator
from eatb.metadata.XmlHelper import q
from eatb.packaging.package_creator import create_package

logger = logging.getLogger(__name__)


def create_aip(package_dir, identifier, package_name, identifier_map=None, generate_premis=True,
               generate_package=True) -> bool:

    # schema file location for Mets generation
    schemas = os.path.join(ROOT, 'resources/schemas')

    # for every REPRESENTATION without METS file:
    for repdir in os.listdir(os.path.join(package_dir, 'representations')):
        rep_path = os.path.join(package_dir, 'representations/%s' % repdir)
        # TODO: packageid?
        # parent = task_context.additional_data['parent_id']
        mets_data = {'packageid': repdir,
                     'type': "AIP",
                     'schemas': schemas,
                     'parent': ''}
        metsgen = MetsGenerator(rep_path)
        metsgen.createMets(mets_data)

        logger.info('Generated a Mets file for representation %s.' % repdir)

    #########

    # schema file location for Mets generation
    schemas = os.path.join(package_dir, 'schemas')

    mets_data = {'packageid': identifier,
                 'type': "AIP",
                 'schemas': schemas,
                 'parent': None}

    metsgen = MetsGenerator(package_dir)
    metsgen.createMets(mets_data)

    # TODO: get structMap from submission root METS, translate SIP packagename to
    # AIP UUID and add it to the AIP root METS

    # get identifier_map
    if identifier_map:
        # check if packagename is in the identifier map
        if package_name in identifier_map:
            identifier = identifier_map[package_name]
            logger.info("Provided identifier assigned: %s" % identifier)
        else:
            logger.error("Cannot find uuid for package name %s in provided identifier_map" % package_name)


        METS_NS = 'http://www.loc.gov/METS/'
        XLINK_NS = "http://www.w3.org/1999/xlink"

        # parse submission SIP mets
        parser = etree.XMLParser(resolve_entities=False, remove_blank_text=True, strip_cdata=False)
        sip_mets_path = os.path.join(package_dir, 'submission', 'METS.xml')
        # print sip_mets_path
        sip_parse = etree.parse(sip_mets_path, parser)
        sip_root = sip_parse.getroot()

        # parse package AIP METS and append children and parent structMaps
        aip_mets_path = os.path.join(package_dir, 'METS.xml')
        aip_parse = etree.parse(aip_mets_path, parser)
        aip_root = aip_parse.getroot()

        # get children structMap and replace the urn:uuid:packagename with corresponding urn:uuid:uuid
        children_map = sip_root.find("%s[@LABEL='child %s']" % (q(METS_NS, 'structMap'), 'SIP'))
        if children_map is not None:
            children_map.set('LABEL', 'child AIP')
            children_div = children_map.find("%s[@LABEL='child %s identifiers']" % (q(METS_NS, 'div'), 'SIP'))
            children_div.set('LABEL', 'child AIP identifiers')
            children = children_div.findall("%s[@LABEL='child %s']" % (q(METS_NS, 'div'), 'SIP'))
            for child in children:
                child.set('LABEL', 'child AIP')
                mptr = child.find("%s" % q(METS_NS, 'mptr'))
                urn = mptr.get(q(XLINK_NS, 'href'))
                urn = urn.split('urn:uuid:', 1)[1]
                uuid = identifier_map[urn]
                mptr.set(q(XLINK_NS, 'href'), 'urn:uuid:' + uuid)
                mptr.set(q(XLINK_NS, 'title'), 'Referencing a child AIP.')
            aip_root.append(children_map)
        # get parents structMap and replace the urn:uuid:packagename with corresponding urn:uuid:uuid
        parents_map = sip_root.find("%s[@LABEL='parent %s']" % (q(METS_NS, 'structMap'), 'SIP'))
        if parents_map is not None:
            parents_map.set('LABEL', 'parent AIP')
            parents_div = parents_map.find("%s[@LABEL='parent %s identifiers']" % (q(METS_NS, 'div'), 'SIP'))
            parents_div.set('LABEL', 'parent AIP identifiers')
            parents = parents_div.findall("%s[@LABEL='parent %s']" % (q(METS_NS, 'div'), 'SIP'))
            for parent in parents:
                parent.set('LABEL', 'parent AIP')
                mptr = parent.find("%s" % q(METS_NS, 'mptr'))
                urn = mptr.get(q(XLINK_NS, 'href'))
                urn = urn.split('urn:uuid:', 1)[1]
                uuid = identifier_map[urn]
                mptr.set(q(XLINK_NS, 'href'), 'urn:uuid:' + uuid)
                mptr.set(q(XLINK_NS, 'title'), 'Referencing a parent AIP.')
            aip_root.append(parents_map)

        str = etree.tostring(aip_root, encoding='UTF-8', pretty_print=True, xml_declaration=True)
        with open(aip_mets_path, 'w') as output_file:
            output_file.write(str)

    # packaging
    input_path = Path(package_dir)
    storage_tar_file = os.path.join(input_path.parent, identifier + '.tar')
    if generate_package:
        logger.info("Creating package: %s" % storage_tar_file)
        create_package(package_dir, identifier)

    mets_path = os.path.join(package_dir, "METS.xml")
    if not os.path.exists(mets_path):
        logger.error("Error creating METS file %s" % mets_path)
    else:
        logger.info('Generated a root Mets file: %s.' % mets_path)

    package_success = (not generate_package or os.path.exists(storage_tar_file))
    if not package_success:
        logger.error("Error creating package %s" % storage_tar_file)

    return (
        os.path.exists(mets_path)
        and
        package_success
    )
