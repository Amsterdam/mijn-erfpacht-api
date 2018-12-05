import base64

import requests

from .utils import encrypt
from .config import credentials
from ..tma_utils import get_bsn_from_saml_token


class MijnErfpachtConnection:
    """ This helper class represents the connection to the MijnErfpacht API """

    # URL where to check for erfpacht
    URL = 'https://mijnerfpacht.acc.amsterdam.nl/api/check/groundlease/user/'

    def check_erfpacht(self, saml_token):
        """ Check for erfpacht at MijnErfpacht based on a BSN """
        # Get the BSN from the SAML token
        bsn = get_bsn_from_saml_token(saml_token)

        # Encrypt and decode the bsn
        encrypted = encrypt(bsn)
        encoded_encryption = base64.urlsafe_b64encode(
            encrypted).decode('ASCII')

        # Check the MijnErfpacht API if the BSN has erfpacht
        headers = {'X-API-KEY': credentials['API_KEY']}
        res = requests.get(
            '{}{}'.format(self.URL, encoded_encryption),
            headers=headers
        )

        return res.text
