import os

from flask_restful import abort
from tma_saml import get_digi_d_bsn


def get_bsn_from_request(request):
    """
    Get the BSN based on a request, expecting a SAML token in the headers
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the request with the TMA certificate
    try:
        bsn = get_digi_d_bsn(request, tma_certificate)
    except Exception as e:
        abort(400, message=e)
    return bsn


def get_tma_certificate():
    tma_cert_location = os.getenv('TMA_CERTIFICATE')
    with open(tma_cert_location) as f:
        return f.read()
