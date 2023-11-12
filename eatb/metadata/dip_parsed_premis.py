from lxml import objectify

from eatb.metadata.parsed_premis import ParsedPremis, P
from eatb.utils.XmlHelper import sequence_insert


class DIPPremis(ParsedPremis):
    """
    DIPPremis class
    """

    def __init__(self, f):
        ParsedPremis.__init__(self, f)

    def get_object_by_identifier(self, identifier = None):
        """
        Find the object with the identifier of the package. If this object does not exist, take the first object of the premis file.
        @param identifier:  Identifier of the package
        @return: premis object element
        """
        if not identifier:
            find = objectify.ObjectPath("premis.object")
            return find(self.root)[0]
        xpath_expr = "//*[local-name() = 'object']/descendant::*[local-name() = 'objectIdentifierValue' and text()='%s']/parent::*/parent::*" % identifier
        xpath_result_nodes = self.root.xpath(xpath_expr)
        object_elm = None if len(xpath_result_nodes) != 1 else xpath_result_nodes[0]
        print(len(xpath_result_nodes))
        print("Type: %s" % type(object_elm))
        return object_elm

    def get_event_identifier_by_name(self, event_name):
        """
        Get the identifier of an event with a given name.
        @param event_name:  Name of the
        @return: event identifier value
        """
        find = objectify.ObjectPath("premis.object")
        xpath_expr = "//*[local-name() = 'eventType' and text()='%s']/parent::*/descendant::*[local-name() = 'eventIdentifierValue']" % event_name
        xpath_result_nodes = self.root.xpath(xpath_expr)
        dip_acquire_aips_id = find(self.root) if len(xpath_result_nodes) != 1 else xpath_result_nodes[0].text
        return dip_acquire_aips_id

    def add_related_aips(self, related_aips, related_event_name, identifier = None):
        """
        Add relationship information of AIPs which were used to create the DIP to the premis object of the package.
        @type       related_aips: list[string]
        @param      related_aips: List of related AIP identifiers
        @type       related_event_name: string
        @param      related_event_name: Name of the related event
        @type       identifier: string
        @param      identifier: Identifier of the object to which the elements are added (first object if none given)
        @rtype:     bool
        @return:    Success/failure of adding the related AIP identifiers
        """
        object_node = self.get_object_by_identifier(identifier)

        find = objectify.ObjectPath("object.objectIdentifier.objectIdentifierValue")
        print(find(object_node).text)

        dip_acquire_aips_id = self.get_event_identifier_by_name(related_event_name)
        sequence_number = 1
        for related_aip in related_aips:
            sequence_insert(
                object_node,
                    P.relationship(
                        P.relationshipType('derivation'),
                        P.relationshipSubType('AIP to DIP conversion'),
                        P.relatedObjectIdentification(
                            P.relatedObjectIdentifierType("repository"),
                            P.relatedObjectIdentifierValue(related_aip),
                            P.relatedObjectSequence(str(sequence_number)),
                        ),
                        P.relatedEventIdentification(
                            P.relatedEventIdentifierType("local"),
                            P.relatedEventIdentifierValue(dip_acquire_aips_id),
                        ),
                    ),

                self.premis_successor_sections
            )
            sequence_number += 1
        return True
