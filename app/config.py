import os
import logging

SENTRY_DSN = os.getenv("SENTRY_DSN", None)

credentials = dict(
    ENCRYPTION_VECTOR=os.getenv("MIJN_ERFPACHT_ENCRYPTION_VECTOR"),
    ENCRYPTION_KEY=os.getenv("MIJN_ERFPACHT_ENCRYPTION_KEY"),
    API_KEY=os.getenv("MIJN_ERFPACHT_API_KEY"),
    ENCRYPTION_KEY_V2=os.getenv("MIJN_ERFPACHT_ENCRYPTION_KEY_V2"),
)

API_URL = os.getenv("MIJN_ERFPACHT_API_URL")

logger = logging.getLogger(__name__)

ERFPACHT_API_REQUEST_TIMEOUT = 9


def check_env():
    """
    Checks if all required environment variables have been set
    """
    missing_vars = [
        v
        for v in [
            "MIJN_ERFPACHT_ENCRYPTION_VECTOR",
            "MIJN_ERFPACHT_ENCRYPTION_KEY",
            "MIJN_ERFPACHT_ENCRYPTION_KEY_V2",
            "MIJN_ERFPACHT_API_KEY",
            "TMA_CERTIFICATE",
        ]
        if not os.getenv(v, None)
    ]
    if missing_vars:
        raise Exception(
            "Missing environment variables {}".format(", ".join(missing_vars))
        )
