from base64 import b64decode
from signxml import XMLVerifier
import os

NAMESPACE = '{urn:oasis:names:tc:SAML:2.0:assertion}'
STATEMENT_TAG = '{}AttributeStatement'.format(NAMESPACE)
ATTRIBUTE_TAG = '{}Attribute'.format(NAMESPACE)
ATTR_VALUE_TAG = '{}AttributeValue'.format(NAMESPACE)


class SamlVerificationException(Exception):
    pass


def get_bsn_from_saml_token(saml_token):
    """ Retrieve the SAML token from the request header """

    # return '123443210'

    tma_certificate = get_tma_certificate()

    bsn = verify_saml_token_and_retrieve_attr(
        token=saml_token,
        attr='uid',
        cert=tma_certificate)
    return bsn


def get_tma_certificate():
    """ Get the TMA certificate from a file """
    cwd = os.path.dirname(__file__)
    file_name = "tma-cert.txt"
    file_path = os.path.join(cwd, file_name)
    with open(file_path, 'r') as f:
        return f.read()


def verify_saml_token_and_retrieve_attr(token, cert, attr):
    """ Get an attribute from a SAML token """
    # Check token
    if not token:
        raise SamlVerificationException('Missing SAML token')

    # Verify token
    try:
        verified_data = XMLVerifier().verify(
            b64decode(token),
            x509_cert=cert
        ).signed_xml
        saml_attributes = get_saml_assertion_attributes(verified_data)
    except Exception as e:
        raise SamlVerificationException(e)

    # Check token for attribute
    if attr not in saml_attributes:
        raise SamlVerificationException(
            'Missing attribute \'{}\' in SAML token'.format(attr))

    # Return the attribute
    return saml_attributes[attr]


def get_saml_assertion_attributes(saml_xml):
    statement = saml_xml.find(STATEMENT_TAG)
    return {attrib.attrib['Name']: attrib.find(ATTR_VALUE_TAG).text for attrib in statement.iter(ATTRIBUTE_TAG)}
