import base64

import requests

from api.mijn_erfpacht.utils import encrypt
from api.mijn_erfpacht.config import credentials, API_URL


class MijnErfpachtConnection:
    """ This helper class represents the connection to the MijnErfpacht API """

    def get_from_erfpacht(self, bsn):
        encrypted = encrypt(bsn)
        encoded_encryption = base64.urlsafe_b64encode(
            encrypted).decode('ASCII')

        # Get the api key from env
        key = credentials['API_KEY']
        if not key:
            raise Exception(
                'No api key found in environment variables or key ' +
                'is None/empty string')

        headers = {'X-API-KEY': key}
        res = requests.get(
            '{}{}'.format(API_URL, encoded_encryption),
            headers=headers,
            timeout=12
        )
        return res

    def check_erfpacht(self, bsn):
        """ Check for erfpacht at MijnErfpacht based on a BSN """
        # Encrypt and decode the bsn
        # Check the MijnErfpacht API if the BSN has erfpacht
        # Handle forbidden response

        res = self.get_from_erfpacht(bsn)

        if res.status_code == 403:
            raise Exception(
                'Unable to authenticate to source API. ' +
                'Check if the provided api key is correct and if you are ' +
                'making the request through a whitelisted ' +
                'environment (e.g. secure VPN).')

        # Handle 400 range responses
        if str(res.status_code)[0] == '4':
            raise Exception(
                'The source API responded with 4xx status code, ' +
                'saying: {}'.format(res.text))

        from api.server import app
        app.logger.info(
            'Successfully forwarded request. Response: {}'.format(res.text))

        return {'status': res.text == "true"}
