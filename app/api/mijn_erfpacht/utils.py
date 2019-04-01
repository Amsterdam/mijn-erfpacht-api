from Crypto.Cipher import AES

from api.mijn_erfpacht.config import credentials


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

    # FIXME:
    # Create a random  vector (this is how it should work, but MijnErfPacht
    # works with a static vector)
    # initialization_vector = Random.new().read(AES.block_size)

    # Get the static vector from env
    vector = credentials['ENCRYPTION_VECTOR']
    if not vector:
        raise Exception(
            'No encryption vector found in environment variables or vector ' +
            'is None/empty string')
    try:
        initialization_vector = bytes(
            vector, 'utf-8')
    except Exception as e:
        raise Exception('Unable to use encryption vector. {}'.format(e)) from e

    # Get the encryption key from env
    key = credentials['ENCRYPTION_KEY']
    if not key:
        raise Exception(
            'No encryption key found in environment variables or key ' +
            'is None/empty string')
    try:
        encryption_key = bytes(
            key, 'utf-8')
    except Exception as e:
        raise Exception('Unable to use encryption key. {}'.format(e)) from e

    # Create a AES cipher
    cipher = AES.new(
        key=encryption_key,
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
