import base64

import requests
from app.config import API_KEY, API_URL, ERFPACHT_API_REQUEST_TIMEOUT, logger
from app.utils import encrypt


class MijnErfpachtConnection:
    """This helper class represents the connection to the MijnErfpacht API"""

    def send_request(self, url, additional_headers=None):
        """Check for erfpacht at MijnErfpacht based on a BSN"""

        if not API_KEY:
            raise Exception(
                "No api key found in environment variables or key is None/empty string"
            )

        headers = {"X-API-KEY": API_KEY}
        if additional_headers:
            headers.update(additional_headers)

        res = requests.get(url, headers=headers, timeout=ERFPACHT_API_REQUEST_TIMEOUT)

        logger.debug("Response status: {}, text: {}".format(res.status_code, res.text))

        if res.status_code == 403:
            raise Exception(
                "Unable to authenticate to source API. Check if the provided api key is correct and if you are making the request through a whitelisted environment (e.g. secure VPN)."
            )

        # Handle 400 range responses
        if str(res.status_code)[0] == "4":
            raise Exception(
                "The source API responded with 4xx status code, saying: {}".format(
                    res.text
                )
            )

        return res

    def get_iv_header(self, iv: bytes):
        return {
            "X-RANDOM-IV": iv,
        }

    def get_api_url(
        self,
        encrypted_payload,
        user_type="user",
        operation="check/groundlease",
    ):
        assert user_type in ["user", "company", "kvk", "bsn"]

        payload = base64.urlsafe_b64encode(encrypted_payload).decode("ASCII")

        return f"{API_URL}/api/v2/{operation}/{user_type}/{payload}"

    # Proper encryption with correct IV implementation
    def check_erfpacht_bsn(self, bsn):
        (payload, iv) = encrypt(bsn)
        url = self.get_api_url(payload)
        response = self.send_request(url, self.get_iv_header(iv))
        return response.text == "true"

    def check_erfpacht_kvk(self, kvk_nummer):
        (payload, iv) = encrypt(kvk_nummer)
        url = self.get_api_url(payload, user_type="company")
        response = self.send_request(url, self.get_iv_header(iv))
        return response.text == "true"

    def get_notifications(self, identifier, user_type):
        assert user_type in ["bsn", "kvk"]

        (payload, iv) = encrypt(identifier)
        url = self.get_api_url(payload, user_type=user_type, operation="notifications")

        response = self.send_request(url, self.get_iv_header(iv))

        if response.status_code == 204:
            return []

        return response.json()

    def get_notifications_bsn(self, bsn):
        return self.get_notifications(bsn, "bsn")

    def get_notifications_kvk(self, kvk_number):
        return self.get_notifications(kvk_number, "kvk")
