import os

credentials = dict(
    ENCRYPTION_VECTOR=os.getenv('MIJN_ERFPACHT_ENCRYPTION_VECTOR'),
    ENCRYPTION_KEY=os.getenv('MIJN_ERFPACHT_ENCRYPTION_KEY'),
    API_KEY=os.getenv('MIJN_ERFPACHT_API_KEY')
)

API_URL = os.getenv('MIJN_ERFPACHT_API_URL')
