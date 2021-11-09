import logging
from sys import argv

from app.config import logger
from app.mijn_erfpacht_connection import MijnErfpachtConnection

logger.setLevel(logging.DEBUG)

identifier = argv[1]

con = MijnErfpachtConnection()

has_erfpacht = False
notifications = []

has_erfpacht = con.check_erfpacht_bsn(identifier)


print("has_erfpacht", has_erfpacht)
