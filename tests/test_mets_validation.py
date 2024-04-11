#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

from eatb import ROOT
from eatb.csip_validation import CSIPValidation
from eatb.metadata.mets_validation import MetsValidation

from tests.base import Base
from tests.test_utils import validate


class TestMetsValidation(Base):

    def test_csip1(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=1)
        self.assertTrue(validation_result)

    def test_csip2(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=2)
        self.assertTrue(validation_result)

    def test_csip6(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=6)
        self.assertTrue(validation_result)


    def test_csip117(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=117)
        self.assertTrue(validation_result)

    def test_csip7(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=7)
        self.assertTrue(validation_result)

    def test_csip9(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=9)
        self.assertTrue(validation_result)

    def test_csip10(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=10)
        self.assertTrue(validation_result)

    def test_csip11(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=11)
        self.assertTrue(validation_result)

    def test_csip12(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=12)
        self.assertTrue(validation_result)

    def test_csip13(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=13)
        self.assertTrue(validation_result)

    def test_csip14(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=14)
        self.assertTrue(validation_result)

    def test_csip15(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=15)
        self.assertTrue(validation_result)

    def test_csip16(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=16)
        self.assertTrue(validation_result)

    def test_csip18(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=18)
        self.assertTrue(validation_result)

    def test_csip19(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=19)
        self.assertTrue(validation_result)

    def test_csip22(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=22)
        self.assertTrue(validation_result)

    def test_csip23(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=23)
        self.assertTrue(validation_result)

    def test_csip24(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=24)
        self.assertTrue(validation_result)

    def test_csip25(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=25)
        self.assertTrue(validation_result)

    def test_csip26(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=26)
        self.assertTrue(validation_result)

    def test_csip27(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=27)
        self.assertTrue(validation_result)

    def test_csip28(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=28)
        self.assertTrue(validation_result)

    def test_csip29(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=29)
        self.assertTrue(validation_result)

    def test_csip30(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=30)
        self.assertTrue(validation_result)

    def test_csip33(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=33)
        self.assertTrue(validation_result)

    def test_csip36(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=36)
        self.assertTrue(validation_result)

    def test_csip37(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=37)
        self.assertTrue(validation_result)

    def test_csip38(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=38)
        self.assertTrue(validation_result)

    def test_csip39(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=39)
        self.assertTrue(validation_result)

    def test_csip40(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=40)
        self.assertTrue(validation_result)

    def test_csip41(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=41)
        self.assertTrue(validation_result)

    def test_csip42(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=42)
        self.assertTrue(validation_result)

    def test_csip43(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=43)
        self.assertTrue(validation_result)

    def test_csip44(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=44)
        self.assertTrue(validation_result)

    def test_csip46(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=46)
        self.assertTrue(validation_result)

    def test_csip49(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=49)
        self.assertTrue(validation_result)

    def test_csip50(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=50)
        self.assertTrue(validation_result)

    def test_csip51(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=51)
        self.assertTrue(validation_result)

    def test_csip52(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=52)
        self.assertTrue(validation_result)

    def test_csip53(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=53)
        self.assertTrue(validation_result)

    def test_csip54(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=54)
        self.assertTrue(validation_result)

    def test_csip55(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=55)
        self.assertTrue(validation_result)

    def test_csip56(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=56)
        self.assertTrue(validation_result)

    def test_csip57(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=57)
        self.assertTrue(validation_result)

    def test_csip59(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=59)
        self.assertTrue(validation_result)

    def test_csip113(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=113)
        self.assertTrue(validation_result)

    def test_csip114(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=114)
        self.assertTrue(validation_result)

    def test_csip64(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=64)
        self.assertTrue(validation_result)

    def test_csip65(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=65)
        self.assertTrue(validation_result)

    def test_csip66(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=66)
        self.assertTrue(validation_result)

    def test_csip67(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=67)
        self.assertTrue(validation_result)

    def test_csip68(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=68)
        self.assertTrue(validation_result)

    def test_csip69(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=69)
        self.assertTrue(validation_result)

    def test_csip70(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=70)
        self.assertTrue(validation_result)

    def test_csip71(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=71)
        self.assertTrue(validation_result)

    def test_csip72(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=72)
        self.assertTrue(validation_result)

    def test_csip76(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=76)
        self.assertTrue(validation_result)

    def test_csip77(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=77)
        self.assertTrue(validation_result)

    def test_csip78(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=78)
        self.assertTrue(validation_result)

    def test_csip79(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=79)
        self.assertTrue(validation_result)

    def test_csip80(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=80)
        self.assertTrue(validation_result)

    def test_csip81(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=81)
        self.assertTrue(validation_result)

    def test_csip82(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=82)
        self.assertTrue(validation_result, CSIPValidation._get_rule(self.rules_lines, 82))

    def test_csip83(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=83)
        self.assertTrue(validation_result, self.rules_lines)

    def test_csip84(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=84)
        self.assertTrue(validation_result)

    def test_csip85(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=85)
        self.assertTrue(validation_result)

    def test_csip86(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=86)
        self.assertTrue(validation_result)

    def test_csip88(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=88)
        self.assertTrue(validation_result)

    def test_csip89(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=89)
        self.assertTrue(validation_result)

    def test_csip94(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=94)
        self.assertTrue(validation_result)

    def test_csip96(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=96)
        self.assertTrue(validation_result)

    def test_csip116(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=116)
        self.assertTrue(validation_result)

    def test_csip98(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=98)
        self.assertTrue(validation_result)

    def test_csip100(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=100)
        self.assertTrue(validation_result)

    def test_csip118(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=118)
        self.assertTrue(validation_result)

    def test_csip102(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=102)
        self.assertTrue(validation_result)

    def test_csip104(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=104)
        self.assertTrue(validation_result)

    def test_csip119(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=119)
        self.assertTrue(validation_result)

    def test_csip106(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=106)
        self.assertTrue(validation_result)

    def test_csip107(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=107)
        self.assertTrue(validation_result)

    def test_csip108(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=108)
        self.assertTrue(validation_result)

    def test_csip109(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=109)
        self.assertTrue(validation_result)

    def test_csip110(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=110)
        self.assertTrue(validation_result)

    def test_csip111(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=111)
        self.assertTrue(validation_result)

    def test_csip112(self):
        validation_result, _ = validate(self.rules_lines, self.IP_path + '/METS.xml', rule_id=112)
        self.assertTrue(validation_result)

    def test_IP_mets(self):
        mets_file = 'METS.xml'
        mets_schema_file = os.path.join(ROOT, 'tests/test_resources/schemas/mets_1_11.xsd')
        premis_schema_file = os.path.join(ROOT, 'tests/test_resources/schemas/premis-v3-0.xsd')
        mets_validator = MetsValidation(self.IP_path, mets_schema_file, premis_schema_file)
        mets_validator.validate_mets(os.path.join(self.IP_path, mets_file))


if __name__ == '__main__':
    unittest.main()
