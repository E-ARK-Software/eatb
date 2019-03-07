# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402
from earchivingtoolbox.storage.checksum import ChecksumValidation, ChecksumAlgorithm
from earchivingtoolbox.xml.validationresult import ValidationResult


class DeliveryValidation(object):

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
