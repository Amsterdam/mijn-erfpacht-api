import base64
from unittest.mock import patch

from requests import Timeout
from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt

from app.helpers import decrypt
from app.server import app


class ApiMock:
    status_code = 200
    text = "true"

    def json(self):
        return [
            {
                "title": "Nieuwe factuur met nummer 2",
                "description": "Nieuwe factuur met nummer 2",
                "datePublished": "2020-09-02",
                "link": {
                    "title": "Nieuwe factuur met nummer 2",
                    "to": "/page/groundleases/detail?id=E1/1",
                },
            },
            {
                "title": "Nieuwe factuur met nummer 3",
                "description": "Nieuwe factuur met nummer 3",
                "datePublished": "2020-08-05",
                "link": {
                    "title": "Nieuwe factuur met nummer 3",
                    "to": "/page/groundleases/detail?id=E1/1",
                },
            },
            {
                "title": "Nieuwe factuur met nummer 4",
                "description": "Nieuwe factuur met nummer 4",
                "datePublished": "2020-07-09",
                "link": {
                    "title": "Nieuwe factuur met nummer 4",
                    "to": "/page/groundleases/detail?id=E1/1",
                },
            },
        ]


class TestAPI(FlaskServerTMATestCase):

    TEST_BSN = "111222333"
    TEST_KVK = "90001354"  # kvk nummer taken from https://developers.kvk.nl/documentation/profile-v2-test
    CHECK_ERFPACHT_URL = "/api/erfpacht/v2/check-erfpacht"

    def setUp(self):
        """Setup app for testing"""
        self.client = self.get_tma_test_app(app)
        return app

    # =================================
    # Test the /check-erfpacht endpoint
    # =================================

    @patch("app.mijn_erfpacht_connection.API_KEY", "xxxx")
    @patch("app.helpers.ENCRYPTION_KEY_V2", "xxxx-xxxx-xxxx-xxxx-xxxx-xxxx-xx")
    @patch("app.mijn_erfpacht_connection.requests.get", autospec=True)
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_check_erfpacht_view(self, api_mocked):
        api_mocked.return_value = ApiMock()
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        self.assertEqual(res.status_code, 200, res.data)
        content = res.json["content"]
        self.assertEqual(content["isKnown"], True)
        self.assertEqual(len(content["meldingen"]), 3)

    @patch("app.mijn_erfpacht_connection.API_KEY", "xxxx")
    @patch("app.helpers.ENCRYPTION_KEY_V2", "xxxx-xxxx-xxxx-xxxx-xxxx-xxxx-xx")
    @patch(
        "app.mijn_erfpacht_connection.MijnErfpachtConnection.send_request",
        autospec=True,
    )
    @patch(
        "app.mijn_erfpacht_connection.MijnErfpachtConnection.get_notifications",
        autospec=True,
    )
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_check_erfpacht(self, mocked_check_meldingen, mocked_send_request):
        """
        Test if getting is allowed, if the SAML token is correctly decoded
        and if the MijnErfpachtConnection is called
        """

        res = ApiMock()

        # Mock the MijnErfpacht response
        mocked_send_request.return_value = res
        mocked_check_meldingen.return_value = ApiMock().json()

        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        # Check for a proper response
        self.assertEqual(res.status_code, 200)

        # Check if the mocked method got called with the expected args
        # ANY covers the self argument
        # mocked_send_request.assert_called_once_with(ANY, self.TEST_BSN)
        encrypted_payload = mocked_send_request.call_args[0][1].rsplit("/", 1)[-1]
        additional_headers = mocked_send_request.call_args[0][2]
        iv_header_key = "X-RANDOM-IV"

        self.assertTrue(iv_header_key in additional_headers)

        encrypted_payload = base64.urlsafe_b64decode(encrypted_payload.encode("ASCII"))

        iv = additional_headers[iv_header_key]

        self.assertTrue(decrypt(encrypted_payload, iv) == self.TEST_BSN)

    @patch("app.mijn_erfpacht_connection.API_KEY", "xxxx")
    @patch("app.helpers.ENCRYPTION_KEY_V2", "xxxx-xxxx-xxxx-xxxx-xxxx-xxxx-xx")
    @patch(
        "app.mijn_erfpacht_connection.MijnErfpachtConnection.send_request",
        autospec=True,
    )
    @patch(
        "app.mijn_erfpacht_connection.MijnErfpachtConnection.get_notifications",
        autospec=True,
    )
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_check_erfpacht_kvk(self, mocked_check_meldingen, mocked_send_request):
        """
        Test if getting is allowed, if the SAML token is correctly decoded
        and if the MijnErfpachtConnection is called
        """
        # Mock the MijnErfpacht response
        mocked_send_request.return_value = ApiMock()
        mocked_check_meldingen.return_value = ApiMock().json()

        # Create SAML headers
        SAML_HEADERS = self.add_e_herkenning_headers(self.TEST_KVK)

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        # Check for a proper response
        self.assertEqual(res.status_code, 200)

        encrypted_payload = mocked_send_request.call_args[0][1].rsplit("/", 1)[-1]
        additional_headers = mocked_send_request.call_args[0][2]
        iv_header_key = "X-RANDOM-IV"

        self.assertTrue(iv_header_key in additional_headers)

        encrypted_payload = base64.urlsafe_b64decode(encrypted_payload.encode("ASCII"))

        iv = additional_headers[iv_header_key]

        self.assertTrue(decrypt(encrypted_payload, iv) == self.TEST_KVK)

    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_check_erfpacht_invalid_saml(self):
        """Test if an invalid SAML token gets rejected"""
        # Create SAML headers
        SAML_HEADERS = self.add_digi_d_headers(self.TEST_BSN)

        saml_key = None
        invalid_saml_value = None
        # Invalidate the SAML token
        for k, v in SAML_HEADERS.items():
            saml_key = k
            invalid_saml_value = bytes(str(v)[:-7] + "malware", "utf-8")

        SAML_HEADERS[saml_key] = invalid_saml_value

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        # Check response code
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"message": "Missing SAML token", "status": "ERROR"})

    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_get_check_erfpacht_invalid_bsn(self):
        """Test if an invalid SAML token get rejected"""
        # Create SAML headers with a BSN which doesn't meet the elf proef
        SAML_HEADERS = self.add_digi_d_headers("123456789")

        # Call the API with SAML headers
        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)

        # Check response code
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json, {"message": "Invalid BSN", "status": "ERROR"})

    # raise the requests' Timeout Exception
    @patch("app.mijn_erfpacht_connection.API_KEY", "xxxx")
    @patch("app.helpers.ENCRYPTION_KEY_V2", "xxxx-xxxx-xxxx-xxxx-xxxx-xxxx-xx")
    @patch("app.mijn_erfpacht_connection.requests.get", side_effect=Timeout)
    @patch("app.helpers.get_tma_certificate", lambda: server_crt)
    def test_timeout(self, timeout_mock):
        """Test the response when the connection times out"""
        SAML_HEADERS = self.add_e_herkenning_headers(self.TEST_KVK)

        res = self.client.get(self.CHECK_ERFPACHT_URL, headers=SAML_HEADERS)
        self.assertEqual(res.status_code, 500)
        self.assertEqual(res.json, {"status": "ERROR", "message": "Timeout"})

    def test_health_page(self):
        """Test if the health page lives"""
        res = self.client.get("/status/health")
        self.assertEqual(res.json, "OK")
