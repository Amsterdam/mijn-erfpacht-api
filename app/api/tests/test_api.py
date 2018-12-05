from unittest import TestCase
from unittest.mock import patch, ANY

from ..server import app

MijnErfpachtConnectionLocation = 'app.api.mijn_erfpacht.mijn_erfpacht_' \
                                 'connection.MijnErfpachtConnection'


class TestAPI(TestCase):

    def setUp(self):
        """ Setup app for testing """
        app.config['TESTING'] = True
        self.client = app.test_client()
        return app

    def test_swagger(self):
        """ Test if swagger lives """
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

    @patch(MijnErfpachtConnectionLocation + '.check_erfpacht', autospec=True)
    def test_get_check_erfpacht(self, mocked_method):
        """
        Test the check-erfpacht endpoint and check if the MijnErfpachtConnection
        is correctly called
        """
        # Mock the MijnErfpacht response
        mocked_method.return_value = 'true'

        # The API expects a SAML token added by the TMA middleware in production
        # Here we just add in to the request
        saml_token = 'sometoken'
        res = self.client.get(
            '/check-erfpacht', headers={'x-saml-attribute-token1': saml_token})

        self.assertEqual(res.status_code, 200)

        # ANY covers the self argument
        mocked_method.assert_called_once_with(ANY, saml_token)

    def test_post_check_erfpacht(self):
        """ Test if posting is not allowed """
        res = self.client.post('/check-erfpacht')

        self.assertEqual(res.status_code, 405)

    def test_update_check_erfpacht(self):
        """ Test if updating is not allowed """
        res = self.client.put('/check-erfpacht')

        self.assertEqual(res.status_code, 405)

        res = self.client.patch('/check-erfpacht')

        self.assertEqual(res.status_code, 405)

    def test_delete_check_erfpacht(self):
        """ Test if deleting is not allowed """
        res = self.client.delete('/check-erfpacht')

        self.assertEqual(res.status_code, 405)
