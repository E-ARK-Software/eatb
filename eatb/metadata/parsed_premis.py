#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import objectify
from eatb.utils.XmlHelper import sequence_insert

from datetime import datetime

from lxml import etree, objectify

from eatb.utils.XmlHelper import q, XSI_NS

PREMIS_NS = 'http://www.loc.gov/premis/v3'
PREMIS_NSMAP = {None: PREMIS_NS}
P = objectify.ElementMaker(
    annotate=False,
    namespace=PREMIS_NS,
    nsmap=PREMIS_NSMAP)


class ParsedPremis:

    premis_successor_sections = ['object', 'event', 'agent', 'right']

    def __init__(self, f=None):
        if f is None:
            self.root = P.premis(
                {q(XSI_NS, 'schemaLocation'): PREMIS_NS + ' ../schemas/premis-3-0.xsd'},
            )
            self.root.set('version', '2.0')
        else:
            self.root = objectify.parse(f).getroot()

    def add_object(self, identifier_value):
        sequence_insert(
            self.root, P.object(
                {q(XSI_NS, 'type'): 'file'},
                P.objectIdentifier(
                    P.objectIdentifierType('LOCAL'),
                    P.objectIdentifierValue(identifier_value)
                ),
                P.objectCharacteristics(
                    P.compositionLevel(0),
                    P.format(
                        P.formatRegistry(
                            P.formatRegistryName(),
                            P.formatRegistryKey
                        )
                    )
                )
            ),
            self.premis_successor_sections
        )

    def add_event(self, identifier_value, outcome, linking_agent, linking_object=None):
        sequence_insert(
            self.root, P.event(
                P.eventIdentifier(
                    P.eventIdentifierType('LOCAL'),
                    P.eventIdentifierValue(identifier_value)
                ),
                P.eventType,
                P.eventDateTime(datetime.utcnow().isoformat()),
                P.eventOutcomeInformation(
                    P.eventOutcome(outcome)
                ),
                P.linkingAgentIdentifier(
                    P.linkingAgentIdentifierType('LOCAL'),
                    P.linkingAgentIdentifierValue(linking_agent)
                ),

                P.linkingAgentIdentifier(
                    P.linkingAgentIdentifierType('LOCAL'),
                    P.linkingAgentIdentifierValue(linking_object)
                )
                if linking_object is not None else None
            ),
            self.premis_successor_sections
        )

    def add_agent(self, identifier_value):
        sequence_insert(
            self.root, P.agent(
                P.agentIdentifier(
                    P.agentIdentifierType('LOCAL'),
                    P.agentIdentifierValue(identifier_value)
                ),
                P.agentName('E-ARK AIP to DIP Converter'),
                P.agentType('Software')
            ),
            self.premis_successor_sections
        )

    def __str__(self):
        return etree.tostring(self.root, encoding='UTF-8', pretty_print=True, xml_declaration=True)

    def to_string(self):
        return self.__str__()


