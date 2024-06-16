import os
import csv
from django.conf import settings
from django.core.management.base import BaseCommand
#from django_extensions.db.models import Employee, Department 
from insa.models import Employee, Department 
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
from datetime import datetime

shift=3

class Command(BaseCommand):
    help = 'Key Create'

    def add_arguments(self, parser):
        parser.add_argument('key', type=str, help='License Key')

    def handle(self, *args, **kwargs):
        date_obj = datetime.strptime(kwargs['key'], '%Y-%m-%d')
        encrypted_date = ''

        for part in [date_obj.year, date_obj.month, date_obj.day]:
            for char in str(part):
                encrypted_date += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
            encrypted_date += '-'
    
        encrypted_date = encrypted_date.rstrip('-')
    
        encrypted_date_bytes = encrypted_date.encode('utf-8')
        base64_bytes = base64.b64encode(encrypted_date_bytes)
        base64_encrypted_date = base64_bytes.decode('utf-8')
    
        return base64_encrypted_date
