import base64
from unittest.mock import patch

from requests import Timeout

from app.auth import PROFILE_TYPE_COMMERCIAL, FlaskServerTestCase
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


class TestAPI(FlaskServerTestCase):

    app = app

    CHECK_ERFPACHT_URL = "/api/erfpacht/v2/check-erfpacht"

    # =================================
    # Test the /check-erfpacht endpoint
    # =================================

    @patch("app.mijn_erfpacht_service.API_KEY", "xxxx")
    @patch("app.helpers.ENCRYPTION_KEY_V2", "xxxx-xxxx-xxxx-xxxx-xxxx-xxxx-xx")
    @patch("app.mijn_erfpacht_service.requests.get", autospec=True)
    def test_get_check_erfpacht_view(self, api_mocked):
        api_mocked.return_value = ApiMock()

        # Call the API with SAML headers
        res = self.get_secure(self.CHECK_ERFPACHT_URL)

        self.assertEqual(res.status_code, 200, res.data)
        content = res.json["content"]
        self.assertEqual(content["isKnown"], True)
        self.assertEqual(len(content["notifications"]), 3)

    @patch("app.mijn_erfpacht_service.API_KEY", "xxxx")
    @patch("app.helpers.ENCRYPTION_KEY_V2", "xxxx-xxxx-xxxx-xxxx-xxxx-xxxx-xx")
    @patch(
        "app.mijn_erfpacht_service.MijnErfpachtConnection.send_request",
        autospec=True,
    )
    @patch(
        "app.mijn_erfpacht_service.MijnErfpachtConnection.get_notifications",
        autospec=True,
    )
    def test_get_check_erfpacht(self, mocked_check_meldingen, mocked_send_request):
        """
        Test if getting is allowed, if the SAML token is correctly decoded
        and if the MijnErfpachtConnection is called
        """

        res = ApiMock()

        # Mock the MijnErfpacht response
        mocked_send_request.return_value = res
        mocked_check_meldingen.return_value = ApiMock().json()

        # Call the API with SAML headers
        res = self.get_secure(self.CHECK_ERFPACHT_URL)

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

    @patch("app.mijn_erfpacht_service.API_KEY", "xxxx")
    @patch("app.helpers.ENCRYPTION_KEY_V2", "xxxx-xxxx-xxxx-xxxx-xxxx-xxxx-xx")
    @patch(
        "app.mijn_erfpacht_service.MijnErfpachtConnection.send_request",
        autospec=True,
    )
    @patch(
        "app.mijn_erfpacht_service.MijnErfpachtConnection.get_notifications",
        autospec=True,
    )
    def test_get_check_erfpacht_kvk(self, mocked_check_meldingen, mocked_send_request):
        """
        Test if getting is allowed, if the SAML token is correctly decoded
        and if the MijnErfpachtConnection is called
        """
        # Mock the MijnErfpacht response
        mocked_send_request.return_value = ApiMock()
        mocked_check_meldingen.return_value = ApiMock().json()

        # Call the API with SAML headers
        res = self.get_secure(
            self.CHECK_ERFPACHT_URL, profile_type=PROFILE_TYPE_COMMERCIAL
        )

        # Check for a proper response
        self.assertEqual(res.status_code, 200)

        encrypted_payload = mocked_send_request.call_args[0][1].rsplit("/", 1)[-1]
        additional_headers = mocked_send_request.call_args[0][2]
        iv_header_key = "X-RANDOM-IV"

        self.assertTrue(iv_header_key in additional_headers)

        encrypted_payload = base64.urlsafe_b64decode(encrypted_payload.encode("ASCII"))

        iv = additional_headers[iv_header_key]

        self.assertTrue(decrypt(encrypted_payload, iv) == self.TEST_KVK)

    def test_status(self):
        response = self.client.get("/status/health")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], "OK")
