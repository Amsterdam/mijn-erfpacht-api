import logging
from app.mijn_erfpacht_connection import MijnErfpachtConnection
from app.config import logger
from pprint import pprint
from sys import argv

identifier = argv[1]
kind = argv[2] if len(argv) >= 3 else None

logger.setLevel(logging.DEBUG)


def get_erfpacht():
    con = MijnErfpachtConnection()

    has_erfpacht = False
    notifications = []

    if kind == "bsn":
        has_erfpacht = con.check_erfpacht_bsn(identifier)
        if has_erfpacht:
            notifications = con.get_notifications_bsn(identifier)
    elif kind == "kvk":
        has_erfpacht = con.check_erfpacht_kvk(identifier)
        if has_erfpacht:
            notifications = con.get_notifications_kvk(identifier)

    return has_erfpacht, notifications
