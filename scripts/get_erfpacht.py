from sys import argv
from app.mijn_erfpacht_service import MijnErfpachtConnection

identifier = argv[1]

con = MijnErfpachtConnection()

has_erfpacht = False
notifications = []

has_erfpacht = con.check_erfpacht_bsn(identifier)

print("has_erfpacht", has_erfpacht)

notifications = con.get_notifications(identifier, "bsn")

print("notifications_erfpacht", notifications)
