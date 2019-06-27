import os


def check_env():
    """
    Checks if all required environment variables have been set
    """
    missing_vars = [v for v in ['MIJN_ERFPACHT_ENCRYPTION_VECTOR', 'MIJN_ERFPACHT_ENCRYPTION_KEY', 'MIJN_ERFPACHT_API_KEY', 'TMA_CERTIFICATE']
                    if not os.getenv(v, None)]
    if missing_vars:
        raise Exception('Missing environment variables {}'.format(', '.join(missing_vars)))
