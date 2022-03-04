#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path

from eatb.metadata.mets.metsgenerator import MetsGenerator
from eatb.metadata.premis.premisgenerator import PremisGenerator
from eatb.packaging.package_creator import create_package

LOGGER = logging.getLogger(__name__)

def create_sip(package_dir: str, package_name: str, identifier: str, generate_premis: bool=True,
               generate_package: bool=True, custom_logger=None) -> bool:

    logger = custom_logger if custom_logger else LOGGER

    # PREMIS
    premis_path = os.path.join(package_dir, 'metadata/preservation/premis.xml')
    if generate_premis:
        premisgen = PremisGenerator(package_dir)

        premisgen.createPremis()
        premisinfo = {'outcome': 'success',
                      'task_name': 'create_sip',
                      'event_type': 'Package initialisation',
                      'linked_object': None}

        logger.info("Creating PREMIS file %s" % premis_path)
        premisgen.addEvent('metadata/preservation/premis.xml', premisinfo)

    reps_path = os.path.join(package_dir, 'representations')
    for name in os.listdir(reps_path):
        rep_path = os.path.join(reps_path, name)
        if os.path.isdir(rep_path):
            if generate_premis:
                # representation PREMIS
                logger.info(
                    "Creating representation PREMIS file %s" %
                    os.path.join(rep_path, 'metadata/preservation/premis.xml'))
                premisgen = PremisGenerator(rep_path)
                premisgen.createPremis()
            # representation METS
            logger.info("Creating representation METS file: %s" % os.path.join(rep_path, "METS.xml"))
            mets_data = {'packageid': package_name,
                         'type': "SIP",
                         'schemas': os.path.join(package_dir, 'schemas'),
                         'parent': ''}
            metsgen = MetsGenerator(rep_path)

            metsgen.createMets(mets_data)
    if generate_premis:
        # PREMIS
        premisgen = PremisGenerator(package_dir)
        premisgen.createPremis()

    # METS
    mets_data = {'packageid': package_name,
                 'type': "SIP",
                 'schemas': os.path.join(package_dir, 'schemas'),
                 'parent': ''}
    mets_path = os.path.join(package_dir, "METS.xml")
    logger.info("Creating METS file %s" % mets_path)
    metsgen = MetsGenerator(package_dir)
    metsgen.createMets(mets_data)

    # packaging
    input_path = Path(package_dir)
    storage_tar_file = os.path.join(input_path.parent, package_name + '.tar')
    if generate_package:
        logger.info("Creating package: %s" % storage_tar_file)
        create_package(package_dir, package_name)

    if not os.path.exists(mets_path):
        logger.error("Error creating METS file %s" % mets_path)
    premis_success = (not generate_package or os.path.exists(premis_path))
    if not premis_success:
        logger.error("Error creating PREMIS file %s" % premis_path)
    package_success = (not generate_package or os.path.exists(storage_tar_file))
    if not package_success:
        logger.error("Error creating package %s" % storage_tar_file)

    return (
        os.path.exists(mets_path)
        and
        premis_success
        and
        package_success
    )
