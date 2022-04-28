import logging
import sentry_sdk

from flask import Flask

from requests.exceptions import HTTPError
from sentry_sdk.integrations.flask import FlaskIntegration

from app import auth, mijn_erfpacht_service
from app.config import (
    IS_DEV,
    SENTRY_DSN,
    CustomJSONEncoder,
)
from app.helpers import (
    error_response_json,
    success_response_json,
    validate_openapi,
)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[FlaskIntegration()], with_locals=False
    )


@app.route("/api/erfpacht/v2/check-erfpacht", methods=["GET"])
@auth.login_required
@validate_openapi
def get_all():
    user = auth.get_current_user()
    content = mijn_erfpacht_service.get_data(user)

    return success_response_json(content)


@app.route("/status/health")
def health_check():
    return success_response_json("OK")


@app.errorhandler(Exception)
def handle_error(error):

    error_message_original = f"{type(error)}:{str(error)}"

    msg_auth_exception = "Auth error occurred"
    msg_request_http_error = "Request error occurred"
    msg_server_error = "Server error occurred"

    logging.exception(error, extra={"error_message_original": error_message_original})

    if IS_DEV:  # pragma: no cover
        msg_auth_exception = error_message_original
        msg_request_http_error = error_message_original
        msg_server_error = error_message_original

    if isinstance(error, HTTPError):
        return error_response_json(
            msg_request_http_error,
            error.response.status_code,
        )
    elif auth.is_auth_exception(error):
        return error_response_json(msg_auth_exception, 401)

    return error_response_json(msg_server_error, 500)


if __name__ == "__main__":  # pragma: no cover
    app.run()
