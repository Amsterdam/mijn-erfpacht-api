import os
import secrets
import string
from datetime import date, datetime
from functools import wraps

import yaml
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import request
from flask.helpers import make_response
from openapi_core import create_spec
from openapi_core.contrib.flask import FlaskOpenAPIRequest, FlaskOpenAPIResponse
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from yaml import load

from app.config import BASE_PATH, ENABLE_OPENAPI_VALIDATION, ENCRYPTION_KEY_V2

openapi_spec = None


def get_openapi_spec():
    global openapi_spec
    if not openapi_spec:
        with open(os.path.join(BASE_PATH, "openapi.yml"), "r") as spec_file:
            spec_dict = load(spec_file, Loader=yaml.Loader)

        openapi_spec = create_spec(spec_dict)

    return openapi_spec


def validate_openapi(function):
    @wraps(function)
    def validate(*args, **kwargs):

        if ENABLE_OPENAPI_VALIDATION:
            spec = get_openapi_spec()
            openapi_request = FlaskOpenAPIRequest(request)
            validator = RequestValidator(spec)
            result = validator.validate(openapi_request)
            result.raise_for_errors()

        response = function(*args, **kwargs)

        if ENABLE_OPENAPI_VALIDATION:
            openapi_response = FlaskOpenAPIResponse(response)
            validator = ResponseValidator(spec)
            result = validator.validate(openapi_request, openapi_response)
            result.raise_for_errors()

        return response

    return validate


def success_response_json(response_content):
    return make_response({"status": "OK", "content": response_content}, 200)


def error_response_json(message: str, code: int = 500):
    return make_response({"status": "ERROR", "message": message}, code)


def to_date(date_input):
    if isinstance(date_input, date):
        return date_input

    if isinstance(date_input, datetime):
        return date_input.date()

    if "T" in date_input:
        return datetime.strptime(date_input, "%Y-%m-%dT%H:%M:%S").date()

    return datetime.strptime(date_input, "%Y-%m-%d").date()


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
    if not ENCRYPTION_KEY_V2:
        raise Exception(
            "No encryption key found in environment variables or key is None/empty string"
        )

    encryption_key = bytes(ENCRYPTION_KEY_V2, "utf-8")

    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted), AES.block_size).decode("utf-8")
