import sentry_sdk
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
from flasgger import Swagger

from api.config import check_env, SENTRY_DSN
from api.mijn_erfpacht.mijn_erfpacht_connection import MijnErfpachtConnection
from api.tma_utils import get_bsn_from_request, get_kvk_number_from_request

# Check the environment, will raise an exception if the server is not supplied with sufficient info
from sentry_sdk.integrations.flask import FlaskIntegration
from tma_saml import SamlVerificationException

check_env()

# Init app and set CORS
app = Flask(__name__)
api = Api(app)
CORS(app=app)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FlaskIntegration()],
        with_locals=True
    )

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
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/api/erfpacht/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
            "title": "MijnErfpacht API Client"
        }
    ],
    "static_url_path": "/api/erfpacht/static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/api/erfpacht"
}
swagger = Swagger(app, config=swagger_config)

# Init connection to mijn erfpacht
con = MijnErfpachtConnection()


class ErfpachtCheck(Resource):
    """ Class representing the 'api/erfpacht/check-erfpacht' endpoint"""

    def get(self):
        """
        Check if a citizen has erfpacht based on a BSN
        ---
        responses:
          200:
            description: Erfpacht successfully checked
            type: boolean
            example: True
          400:
            description: Invalid SAML or BSN
        """
        parser = reqparse.RequestParser()
        token_arg_name = 'x-saml-attribute-token1'
        parser.add_argument(
            token_arg_name,
            location='headers',
            required=True,
            help='SAML token required'
        )
        kvk_nummer = None

        try:
            kvk_nummer = get_kvk_number_from_request(request)
            return con.check_erfpacht_kvk(kvk_nummer)
        except SamlVerificationException:
            return {'status': 'ERROR', 'message': 'Missing SAML token'}, 400
        except KeyError:
            # does not contain kvk number, might still contain BSN
            pass

        bsn = get_bsn_from_request(request)
        return con.check_erfpacht_bsn(bsn)


class Health(Resource):
    """ Used in deployment to check if the API lives """

    def get(self):
        return 'OK'


# Add resources to the api
api.add_resource(ErfpachtCheck, '/api/erfpacht/check-erfpacht')
api.add_resource(Health, '/status/health')

if __name__ == '__main__':
    app.run()
