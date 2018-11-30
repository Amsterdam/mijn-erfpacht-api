import base64

import requests

from .utils import encrypt
from .config import credentials


class MijnErfpachtConnection:
    """ This helper class represents the connection to the MijnErfpacht API """

    # URL where to check for erfpacht
    URL = 'https://mijnerfpacht.acc.amsterdam.nl/api/check/groundlease/user/'

    def check_erfpacht(self, bsn):
        """ Check for erfpacht at MijnErfpacht based on a BSN """
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
