import logging
from sys import argv

from app.config import logger
from app.mijn_erfpacht_connection import MijnErfpachtConnection

logger.setLevel(logging.DEBUG)

identifier = argv[1]
kind = argv[2] if len(argv) >= 3 else None


con = MijnErfpachtConnection()

has_erfpacht = False
notifications = []

if kind == "bsn":
    has_erfpacht = con.check_erfpacht_bsn(identifier)
elif kind == "bsn_v1":
    has_erfpacht = con.check_erfpacht_bsn_v1(identifier)


print("has_erfpacht", has_erfpacht)
