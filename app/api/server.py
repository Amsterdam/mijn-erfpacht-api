from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
from flasgger import Swagger
import simplejson
from .mijn_erfpacht.mijn_erfpacht_connection import MijnErfpachtConnection

# Init app and set CORS
app = Flask(__name__)
api = Api(app)
CORS(app=app)

"""
Info about Swagger
==================

In this app we use Flasgger -> https://github.com/rochacbruno/flasgger
Flasgger provides the possibility to describe swagger per endpoint in the
endpoint's description. These description is automatically collected and merged
into a swagger spec which is exposed on '/'.
"""

# Configure Swagger
swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
            "title": "MijnErfpacht API Client"
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/"
}
swagger = Swagger(app, config=swagger_config)

# Init connection to ZorgNed
con = MijnErfpachtConnection()


class ErfpachtCheck(Resource):
    """ Class representing the '/check-erfpacht' endpoint"""

    def get(self):
        """
        Check if a citizen has erfpacht based on a BSN
        ---
        parameters:
          - name: BSN
            type: string
            description: The BSN for which the voorzieningen should be fetched
        responses:
          200:
            description: Erfpacht successfully checked
            type: object
            example: True
          401:
            description: Invalid authentication token
          403:
            description: Disabled functionality
          404:
            description: Unknown BSN
        """
        parser = reqparse.RequestParser()
        parser.add_argument('bsn')
        bsn = parser.parse_args()['bsn']
        bsn = '123443210'
        # return simplejson.dumps(con.check_erfpacht(bsn))
        con.check_erfpacht(bsn)


# Add resources to the api
api.add_resource(ErfpachtCheck, '/check-erfpacht')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
