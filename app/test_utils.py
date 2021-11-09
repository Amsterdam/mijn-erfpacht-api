from unittest import TestCase
from app.utils import encrypt, decrypt


class TestUtils(TestCase):
    def test_encryption(self):
        (encrypted, iv) = encrypt("TEST")
        self.assertEqual("TEST", decrypt(encrypted, iv))
