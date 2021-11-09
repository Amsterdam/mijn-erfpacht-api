import sentry_sdk
from flasgger import Swagger
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse

# Check the environment, will raise an exception if the server is not supplied with sufficient info
from requests import ConnectionError, Timeout
from sentry_sdk.integrations.flask import FlaskIntegration
from tma_saml import InvalidBSNException, SamlVerificationException

from app.config import SENTRY_DSN, logger
from app.mijn_erfpacht_connection import MijnErfpachtConnection
from app.tma_utils import get_bsn_from_request, get_kvk_number_from_request

# Init app and set CORS
app = Flask(__name__)
api = Api(app)
CORS(app=app)

if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FlaskIntegration()], with_locals=True)


"""
Info about Swagger
==================

In this app we use Flasgger -> https://github.com/rochacbruno/flasgger
Flasgger provides the possibility to describe swagger per endpoint in the
endpoint's description. These description is automatically collected and merged
into a swagger spec which is exposed on '/api/erfpacht/'.
"""
# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/api/erfpacht/apispec_1.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
            "title": "MijnErfpacht API Client",
        }
    ],
}
swagger = Swagger(app, config=swagger_config)

# Init connection to mijn erfpacht
con = MijnErfpachtConnection()


def get_data(kind, identifier):
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


class ErfpachtCheckv2(Resource):
    def get(self):
        kind = None
        identifier = None

        try:
            identifier = get_kvk_number_from_request(request)
            kind = "kvk"
        except SamlVerificationException:
            return {"status": "ERROR", "message": "Missing SAML token"}, 400
        except KeyError:
            # does not contain kvk number, might still contain BSN
            pass

        if not identifier:
            try:
                identifier = get_bsn_from_request(request)
            except InvalidBSNException:
                return {"status": "ERROR", "message": "Invalid BSN"}, 400
            kind = "bsn"

        try:
            has_erfpacht, notifications = get_data(kind, identifier)
        except Timeout:
            return {"status": "ERROR", "message": "Timeout"}, 500
        except ConnectionError as e:
            logger.error(f"ConnectionError {e}")
            return {"status": "ERROR", "message": "Connection Error"}, 500
        except Exception as e:
            logger.exception(e)
            return {"status": "ERROR", "message": "Unknown error"}, 500

        return {
            "status": "OK",
            "content": {
                "isKnown": has_erfpacht,
                "meldingen": notifications,
            },
        }


class Health(Resource):
    """Used in deployment to check if the API lives"""

    def get(self):
        return "OK"


# Add resources to the api
api.add_resource(ErfpachtCheckv2, "/api/erfpacht/v2/check-erfpacht")
api.add_resource(Health, "/status/health")

if __name__ == "__main__":
    app.run()
