from django.core.signing import Signer
from django.conf import settings

def generate_license_key():
    signer = Signer()
    license_key = signer.sign("license_key")
    return license_key
