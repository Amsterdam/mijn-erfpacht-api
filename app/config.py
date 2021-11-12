import os
import logging

SENTRY_DSN = os.getenv("SENTRY_DSN", None)
API_KEY = os.getenv("MIJN_ERFPACHT_API_KEY")
ENCRYPTION_KEY_V2 = os.getenv("MIJN_ERFPACHT_ENCRYPTION_KEY_V2")
API_URL = os.getenv("MIJN_ERFPACHT_API_URL")
ERFPACHT_API_REQUEST_TIMEOUT = 9

logger = logging.getLogger(__name__)
