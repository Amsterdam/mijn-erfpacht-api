from unittest import TestCase
from app.helpers import encrypt, decrypt


class TestHelpers(TestCase):
    def test_encryption(self):
        (encrypted, iv) = encrypt("TEST")
        self.assertEqual("TEST", decrypt(encrypted, iv))
