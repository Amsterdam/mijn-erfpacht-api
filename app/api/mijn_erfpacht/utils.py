import base64

from urllib import parse
from Crypto.Cipher import AES
from Crypto import Random

from .config import credentials


def encrypt(plaintext):
    """
    Encrypt text based on the MijnErfpacht key and vector

    The MijnErfpacht API encrypts as follows (in Java):

    # String initVector = credentials.VECTOR
    # String keyValue = credentialss.ENCRYPTION_KEY
    #
    # IvParameterSpec iv = new IvParameterSpec(initVector.getBytes("UTF-8"))
    # SecretKeySpec skeySpec = new SecretKeySpec(
    #   keyValue.getBytes("UTF-8"), "AES"
    # )
    # Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5PADDING")
    # cipher.init(Cipher.ENCRYPT_MODE, skeySpec, iv)
    #
    # byte[] encrypted = cipher.doFinal(data.getBytes())
    # return Base64.encodeBase64String(encrypted)
    """
    # Create a randam  vector (this is how it should work, but MijnErfPacht
    # works with a static vector)
    # initialization_vector = Random.new().read(AES.block_size)

    # Set the static vector from env
    initialization_vector = bytes(credentials['ENCRYPTION_VECTOR'], 'utf-8')

    # Create a AES cipher
    cipher = AES.new(
        key=bytes(credentials['ENCRYPTION_KEY'], 'utf-8'),
        mode=AES.MODE_CBC,
        IV=initialization_vector
    )

    # Apply padding to the plaintext
    padded_plaintext = pad_pkcs7(bytes(plaintext, 'utf-8'))

    # Encrypt the whole thing and return
    return cipher.encrypt(padded_plaintext)


def pad_pkcs7(data_to_pad):
    """
    Apply PKCS7 padding
    """
    padding_len = AES.block_size - len(data_to_pad) % AES.block_size
    padding = chr(padding_len).encode('ASCII') * padding_len
    return data_to_pad + padding
