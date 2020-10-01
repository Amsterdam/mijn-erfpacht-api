import base64

import requests

from api.mijn_erfpacht.utils import encrypt
from api.mijn_erfpacht.config import credentials, API_URL


class MijnErfpachtConnection:
    """ This helper class represents the connection to the MijnErfpacht API """

    def _make_request(self, url: str, identifier: str):
        """
        Make a request to url with the encrypted identifier concatted at the end.
        :param url:
        :param identifier: BSN or KVK number
        :return:
        """
        encrypted = encrypt(identifier)
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
            f'{url}/{encoded_encryption}',
            headers=headers,
            timeout=9
        )
        return res

    def check_erfpacht_bsn(self, bsn):
        return self.check_erfpacht(bsn, 'user')

    def check_erfpacht_kvk(self, kvk_nummer):
        return self.check_erfpacht(kvk_nummer, 'company')

    def check_erfpacht(self, identifier, kind='user'):
        """ Check for erfpacht at MijnErfpacht based on a BSN """
        # Encrypt and decode the bsn
        # Check the MijnErfpacht API if the BSN has erfpacht
        # Handle forbidden response
        assert kind in ['user', 'company']
        url = f'{API_URL}/api/check/groundlease/{kind}'
        res = self._make_request(url, identifier)

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

        return res.text == "true"

    def get_notifications_bsn(self, bsn):
        return self.get_notifications(bsn, 'bsn')

    def get_notifications_kvk(self, kvk_number):
        return self.get_notifications(kvk_number, 'kvk')

    def get_notifications(self, identifier, kind):
        assert kind in ['bsn', 'kvk']

        url = f'{API_URL}/api/notifications/{kind}'

        res = self._make_request(url, identifier)
        if res.status_code == 204:
            return []
        res_json = res.json()
        return res_json
