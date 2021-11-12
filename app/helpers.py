import os
import secrets
import string

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tma_saml import HR_KVK_NUMBER_KEY, get_digi_d_bsn, get_e_herkenning_attribs

from app.config import ENCRYPTION_KEY_V2


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


def get_bsn_from_request(request):
    """
    Get the BSN based on a request, expecting a SAML token in the headers
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the request with the TMA certificate
    bsn = get_digi_d_bsn(request, tma_certificate)
    return bsn


def get_kvk_number_from_request(request):
    """
    Get the KVK number from the request headers.
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the request with the TMA certificate
    attribs = get_e_herkenning_attribs(request, tma_certificate)
    kvk = attribs[HR_KVK_NUMBER_KEY]
    return kvk


def get_tma_certificate():
    tma_cert_location = os.getenv("TMA_CERTIFICATE")
    with open(tma_cert_location) as f:
        return f.read()
