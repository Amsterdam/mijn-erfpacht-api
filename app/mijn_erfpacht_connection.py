import base64

import requests
from app.config import API_URL, ERFPACHT_API_REQUEST_TIMEOUT, credentials, logger
from app.utils import get_encrypted_payload


class MijnErfpachtConnection:
    """This helper class represents the connection to the MijnErfpacht API"""

    def send_request(self, url, additional_headers=None):
        """Check for erfpacht at MijnErfpacht based on a BSN"""

        key = credentials["API_KEY"]
        if not key:
            raise Exception(
                "No api key found in environment variables or key is None/empty string"
            )

        headers = {"X-API-KEY": key}
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
            "X-RANDOM-IV": str(iv),
            "X-API-KEY": credentials["API_KEY_V2"],
        }

    def get_api_url(
        self,
        encrypted_payload,
        version=2,
        user_type="user",
        operation="check/groundlease",
    ):
        assert user_type in ["user", "company", "kvk", "bsn"]

        payload = base64.urlsafe_b64encode(encrypted_payload).decode("ASCII")

        if version != 1:
            version = f"/v{version}"
        else:
            version = ""

        return f"{API_URL}/api{version}/{operation}/{user_type}/{payload}"

    # Initial encryption
    def check_erfpacht_bsn_v1(self, bsn):
        (payload, iv) = get_encrypted_payload(bsn, version=1)
        url = self.get_api_url(payload, version=1)
        response = self.send_request(url)
        return response.text == "true"

    def check_erfpacht_kvk_v1(self, kvk_nummer):
        (payload, iv) = get_encrypted_payload(kvk_nummer, version=1)
        url = self.get_api_url(payload, version=1, user_type="company")
        response = self.send_request(url)
        return response.text == "true"

    def get_notifications_v1(self, identifier, user_type):
        assert user_type in ["bsn", "kvk"]

        (payload, iv) = get_encrypted_payload(identifier, version=1)
        url = self.get_api_url(
            payload, user_type=user_type, operation="notifications", version=1
        )

        response = self.send_request(url)

        if response.status_code == 204:
            return []

        return response.json()

    def get_notifications_bsn_v1(self, bsn):
        return self.get_notifications_v1(bsn, "bsn")

    def get_notifications_kvk_v1(self, kvk_number):
        return self.get_notifications_v1(kvk_number, "kvk")

    # Proper encryption with correct IV implementation
    def check_erfpacht_bsn(self, bsn):
        (payload, iv) = get_encrypted_payload(bsn)
        url = self.get_api_url(payload)
        response = self.send_request(url, self.get_iv_header(iv))
        return response.text == "true"

    def check_erfpacht_kvk(self, kvk_nummer):
        (payload, iv) = get_encrypted_payload(kvk_nummer)
        url = self.get_api_url(payload, user_type="company")
        response = self.send_request(url, self.get_iv_header(iv))
        return response.text == "true"

    def get_notifications(self, identifier, user_type):
        assert user_type in ["bsn", "kvk"]

        (payload, iv) = get_encrypted_payload(identifier)
        url = self.get_api_url(payload, user_type=user_type, operation="notifications")

        response = self.send_request(url, self.get_iv_header(iv))

        if response.status_code == 204:
            return []

        return response.json()

    def get_notifications_bsn(self, bsn):
        return self.get_notifications(bsn, "bsn")

    def get_notifications_kvk(self, kvk_number):
        return self.get_notifications(kvk_number, "kvk")
