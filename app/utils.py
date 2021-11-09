import secrets
import string

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from app.config import API_KEY, ENCRYPTION_KEY_V2


def encrypt(plaintext):
    """
    Encrypt text based on the MijnErfpacht key and vector
    """

    iv = bytes(
        "".join(
            secrets.choice(string.ascii_uppercase + string.ascii_lowercase)
            for i in range(AES.block_size)
        ),
        "utf-8",
    )

    if not ENCRYPTION_KEY_V2:
        raise Exception(
            "No encryption key found in environment variables or key is None/empty string"
        )

    encryption_key = bytes(ENCRYPTION_KEY_V2, "utf-8")
    cipher = AES.new(key=encryption_key, mode=AES.MODE_CBC, IV=iv)
    padded_plaintext = pad(plaintext.encode("utf-8"), AES.block_size)

    return (cipher.encrypt(padded_plaintext), iv)


def decrypt(encrypted, iv):
    key = ENCRYPTION_KEY_V2

    if not key:
        raise Exception(
            "No encryption key found in environment variables or key is None/empty string"
        )

    encryption_key = bytes(key, "utf-8")

    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted), AES.block_size).decode("utf-8")
