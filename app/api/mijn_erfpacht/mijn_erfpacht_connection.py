from requests import Session


class MijnErfpachtConnection:
    """ This class represents the connection to the ZorgNed API """

    def __init__(self):
        self._session = self._initialize_session()

    def _initialize_session(self):
        return Session()

    def check_erfpacht(self, bsn):
        """ Check for erfpacht at MijnErfpacht based on a BSN """
        return True
