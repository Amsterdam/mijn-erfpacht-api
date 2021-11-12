from unittest import TestCase
from unittest.mock import patch
from app.helpers import encrypt, decrypt


class TestHelpers(TestCase):
    @patch("app.helpers.ENCRYPTION_KEY_V2", "1234567890123456")
    def test_encryption(self):
        (encrypted, iv) = encrypt("TEST")
        self.assertEqual("TEST", decrypt(encrypted, iv))
