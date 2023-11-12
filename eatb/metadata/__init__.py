from lxml import objectify
import logging

METS_NS = 'http://www.loc.gov/METS/'
METSEXT_NS = 'ExtensionMETS'
XLINK_NS = "http://www.w3.org/1999/xlink"
CSIP_NS = "https://DILCIS.eu/XML/METS/CSIPExtensionMETS"
METS_NSMAP = {None: METS_NS, "csip": CSIP_NS, "xlink": "http://www.w3.org/1999/xlink", "ext": METSEXT_NS,
              "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DELIVERY_METS_NSMAP = {None: METS_NS, "csip": CSIP_NS, "xlink": "http://www.w3.org/1999/xlink",
                       "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
PROFILE_XML = "https://earkcsip.dilcis.eu/profile/E-ARK-CSIP.xml"

default_mets_schema_location = 'schemas/mets.xsd'
default_csip_location = "schemas/DILCISExtensionMETS.xsd"
default_xlink_schema_location = 'https://www.w3.org/1999/xlink.xsd'

M = objectify.ElementMaker(
    annotate=False,
    namespace=METS_NS,
    nsmap=METS_NSMAP)

folders_with_USE = ['documentation', 'schemas', 'representations', "data"]

logger = logging.getLogger(__name__)