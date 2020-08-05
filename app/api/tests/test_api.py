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
    text = "true"


class TestAPI(FlaskServerTMATestCase):

    TEST_BSN = '111222333'
    TEST_KVK = '90001354'  # kvk nummer taken from https://developers.kvk.nl/documentation/profile-v2-test
    CHECK_ERFPACHT_URL = '/api/erfpacht/check-erfpacht'

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
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.json, {"status": True})

        test_bsn_encrypted = base64.urlsafe_b64encode(encrypt(self.TEST_BSN)).decode('ASCII')
        call_bsn_encrypted = api_mocked.call_args[0][0].lstrip(os.environ['MIJN_ERFPACHT_API_URL'])

        # check mock if the bsn is encrypted
        self.assertEqual(call_bsn_encrypted, f"/api/check/groundlease/user/{test_bsn_encrypted}")

    @patch(MijnErfpachtConnectionLocation + '.check_erfpacht', autospec=True)
    @patch('api.tma_utils.get_tma_certificate', lambda: server_crt)
    def test_get_check_erfpacht(self, mocked_method):
        """
        Test if getting is allowed, if the SAML token is correctly decoded
        and if the MijnErfpachtConnection is called
        """
        # Mock the MijnErfpacht response
        mocked_method.return_value = 'true'

        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        # Check for a proper response
        self.assertEqual(res.status_code, 200)

        # Check if the mocked method got called with the expected args
        # ANY covers the self argument
        mocked_method.assert_called_once_with(ANY, self.TEST_BSN, 'user')

    @patch(MijnErfpachtConnectionLocation + '.check_erfpacht', autospec=True)
    @patch('api.tma_utils.get_tma_certificate', lambda: server_crt)
    def test_get_check_erfpacht_kvk(self, mocked_method):
        """
        Test if getting is allowed, if the SAML token is correctly decoded
        and if the MijnErfpachtConnection is called
        """
        # Mock the MijnErfpacht response
        mocked_method.return_value = 'true'

        # Create SAML headers
        SAML_HEADERS = self.add_e_herkenning_headers(self.TEST_KVK)

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        # Check for a proper response
        self.assertEqual(res.status_code, 200)

        # Check if the mocked method got called with the expected args
        # ANY covers the self argument
        mocked_method.assert_called_once_with(ANY, self.TEST_KVK, 'company')

    @patch('api.tma_utils.get_tma_certificate', lambda: server_crt)
    def test_get_check_erfpacht_invalid_saml(self):
        """ Test if an invalid SAML token gets rejected """
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        saml_key = None
        invalid_saml_value = None
        # Invalidate the SAML token
        for k, v in SAML_HEADERS.items():
            saml_key = k
            invalid_saml_value = bytes(str(v)[:-7] + 'malware', 'utf-8')

        SAML_HEADERS[saml_key] = invalid_saml_value

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        # Check response code
        self.assertEqual(res.status_code, 400)

    @patch('api.tma_utils.get_tma_certificate', lambda: server_crt)
    def test_get_check_erfpacht_invalid_bsn(self):
        """ Test if an invalid SAML token get rejected """
        # Create SAML headers with a BSN which doesn't meet the elf proef
        SAML_HEADERS = self.add_digi_d_headers('123456789')

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        # Check response code
        self.assertEqual(res.status_code, 400)

    def test_update_check_erfpacht(self):
        """ Test if updating is not allowed """
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.put(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 405)
        res = self.client.patch(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 405)

    def test_post_check_erfpacht(self):
        """ Test if posting is not allowed """
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.post(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 405)

    def test_delete_check_erfpacht(self):
        """ Test if deleting is not allowed """
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        res = self.client.delete(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 405)

    # ============================
    # Test miscellaneous endpoints
    # ============================

    def test_health_page(self):
        """ Test if the health page lives """
        res = self.client.get('/status/health')
        self.assertEqual(res.json, 'OK')

    def test_swagger(self):
        """ Test if swagger lives """
        res = self.client.get('/api/erfpacht')
        self.assertEqual(res.status_code, 200)
