import base64
import os
from unittest.mock import patch, ANY

from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt

os.environ['MIJN_ERFPACHT_ENCRYPTION_VECTOR'] = '1234567890123456'
os.environ['MIJN_ERFPACHT_ENCRYPTION_KEY'] = '1234567890123456'
os.environ['MIJN_ERFPACHT_API_KEY'] = '1234567890123456'
os.environ['TMA_CERTIFICATE'] = __file__  # any file, it should not be used
os.environ['MIJN_ERFPACHT_API_URL'] = 'X'

from api.mijn_erfpacht.utils import encrypt  # noqa: E402
from api.server import app  # noqa: E402

MijnErfpachtConnectionLocation = 'api.mijn_erfpacht.mijn_erfpacht_connection.MijnErfpachtConnection'


class ApiMock:
    status_code = 200
    text = "{}"
    json = {}


class TestAPI(FlaskServerTMATestCase):
    TEST_BSN = '111222333'
    TEST_KVK = '90001354'  # kvk nummer taken from https://developers.kvk.nl/documentation/profile-v2-test
    ERFPACHT_MELDINGEN_URL = '/api/erfpacht/meldingen'

    def setUp(self):
        """ Setup app for testing """
        self.client = self.get_tma_test_app(app)
        return app

    # =================================
    # Test the /check-erfpacht endpoint
    # =================================

    @patch('api.mijn_erfpacht.mijn_erfpacht_connection.requests.get', autospec=True)
    @patch('api.tma_utils.get_tma_certificate', lambda: server_crt)
    def test_get_check_erfpacht_view(self, api_mocked):
        api_mocked.return_value = ApiMock()

        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)
        res = self.client.get(self.ERFPACHT_MELDINGEN_URL, headers=SAML_HEADERS)

        print(res.json)
        self.assertEqual(res.status_code, 200)
