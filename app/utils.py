from app.config import credentials
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.Padding import pad, unpad


def encrypt_v1(plaintext):
    """
    Encrypt text based on the MijnErfpacht key and vector
    """

    key = credentials["ENCRYPTION_KEY"]

    if not key:
        raise Exception(
            "No encryption key found in environment variables or key is None/empty string"
        )

    encryption_key = bytes(key, "utf-8")
    iv = bytes(credentials["ENCRYPTION_VECTOR"], "utf-8")

    # Create a AES cipher
    cipher = AES.new(key=encryption_key, mode=AES.MODE_CBC, IV=iv)

    # Apply padding to the plaintext
    padded_plaintext = pad_pkcs7(bytes(plaintext, "utf-8"))

    # Encrypt the whole thing and return
    return (cipher.encrypt(padded_plaintext), iv)


def encrypt(plaintext):
    """
    Encrypt text based on the MijnErfpacht key and vector
    """

    iv = Random.get_random_bytes(AES.block_size)
    key = credentials["ENCRYPTION_KEY"]

    if not key:
        raise Exception(
            "No encryption key found in environment variables or key is None/empty string"
        )

    encryption_key = bytes(key, "utf-8")

    # Create a AES cipher
    cipher = AES.new(key=encryption_key, mode=AES.MODE_CBC, IV=iv)

    # Apply padding to the plaintext
    padded_plaintext = pad(plaintext.encode("utf-8"), AES.block_size)

    # Encrypt the whole thing and return
    return (cipher.encrypt(padded_plaintext), iv)


def decrypt(encrypted, iv):
    key = credentials["ENCRYPTION_KEY"]

    if not key:
        raise Exception(
            "No encryption key found in environment variables or key is None/empty string"
        )

    encryption_key = bytes(key, "utf-8")

    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted), AES.block_size).decode("utf-8")


def pad_pkcs7(data_to_pad):
    """
    Apply PKCS7 padding
    """
    padding_len = AES.block_size - len(data_to_pad) % AES.block_size
    padding = chr(padding_len).encode("ASCII") * padding_len
    return data_to_pad + padding


def get_encrypted_payload(plaintext, version=2):
    # Get the api key from env
    key = credentials["API_KEY"]
    if not key:
        raise Exception(
            "No api key found in environment variables or key is None/empty string"
        )

    if version == 1:
        return encrypt_v1(plaintext)

    return encrypt(plaintext)
