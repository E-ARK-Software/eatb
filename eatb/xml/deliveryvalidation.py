# -*- coding: utf-8 -*-
import os
import sys
from lxml import etree
from eatb.metadata.mets.ParsedMets import ParsedMets
from eatb.xml.xmlvalidation import XmlValidation

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402
from eatb.storage.checksum import ChecksumValidation, ChecksumAlgorithm
from eatb.xml.validationresult import ValidationResult

import logging
logger = logging.getLogger(__name__)

class DeliveryValidation(object):

    def getFileElements(self, deliveryDir, delivery_xml_file, schema_file):
        log = []
        log.append("Validating delivery: %s using schema: %s" % (delivery_xml_file, schema_file))
        try:
            # Parse the XML file, get the root element
            parsed_mets = ParsedMets(deliveryDir)
            parsed_mets.load_mets(delivery_xml_file)
            # If the XSD file wasn't found, extract location from the XML
            if schema_file == None:
                schema_file = parsed_mets.get_mets_schema_from_schema_location()
            # Parse the XSD file
            parsed_sfile = etree.parse(schema_file)
            # Validate the delivery XML file
            xmlVal = XmlValidation()
            validation_result = xmlVal.validate_XML(parsed_mets.mets_tree, parsed_sfile)
            if validation_result:
                return parsed_mets.get_file_elements()
        except etree.XMLSyntaxError as why:
            logger.error('Error validating delivery %s, why: %s' % (delivery_xml_file, str(why)))
        return None

    def validate_delivery(self, deliveryDir, checksum_file, schema_file, package_file):
        """
        Validate the delivery document.
        level.

        @type       deliveryDir: string
        @param      deliveryDir: Path to delivery directory
        @type       delivery_xml_file:  string
        @param      delivery_xml_file:  Path to delivery file.
        @type       package_file:  string
        @param      package_file:  Path to package file file (e.g. TAR).
        @rtype:     ValidationResult
        @return:    Validation result (validity, process log, error log)
        """
        valid = False
        log = []
        err = []
        valid_checksum = False
        # TODO: define
        checksum_algorithm = ""
        # Checksum validation
        self.get_checksum()
        checksum_expected = self.get_checksum(deliveryDir, checksum_algorithm)
        csval = ChecksumValidation()
        valid_checksum = csval.validate_checksum(package_file, checksum_expected, ChecksumAlgorithm.get(checksum_algorithm))
        log.append("Checksum validity: \"%s\"" % str(valid_checksum))
        valid = (valid_checksum)
        return ValidationResult(valid, log, err)
