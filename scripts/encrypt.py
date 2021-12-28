#!/usr/bin/env python

import base64
from sys import argv

identifier = argv[1]
secret_key = argv[2]

import os

os.environ["MIJN_ERFPACHT_ENCRYPTION_KEY_V2"] = secret_key


from app.helpers import encrypt


(encrypted_string, iv) = encrypt(identifier)

iv_str = iv.decode("utf-8")
payload = base64.urlsafe_b64encode(encrypted_string).decode("ASCII")

print(f"encrypted base64: {payload}, iv: {iv_str}, secret_key: {secret_key}")
